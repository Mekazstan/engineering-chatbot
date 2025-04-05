import time
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from pathlib import Path
from typing import List, Dict, Any
import os
import datetime
import requests
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
from langchain_core.documents import Document

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "tech-docs-index"

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

embeddings_model = CohereEmbeddings(
    model="embed-english-v3.0",
    truncate="END",
    max_retries=3,
)

def embed_chunks_cohere(chunks: List[Any]) -> List[np.ndarray]:
    texts = [chunk.page_content for chunk in chunks]
    try:
        response = requests.post(
            "https://api.cohere.ai/v1/embed",
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "texts": texts,
                "model": "embed-english-v3.0",
                "input_type": "search_document",
                "truncate": "END"
            }
        )
        response.raise_for_status()
        data = response.json()
        return np.array(data['embeddings'])
    except requests.exceptions.RequestException as e:
        print(f"Embedding error: {str(e)}")
        return [np.zeros(1024) for _ in chunks]
    except KeyError as e:
        print(f"Embedding response format error: {str(e)}")
        return [np.zeros(1024) for _ in chunks]

def process_pdf(file_path: Path) -> Dict[str, Any]:
    try:
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        chunks = []
        for page in pages:
            chunks.extend(text_splitter.split_documents([page]))

        max_retries = 3
        embeddings = None
        for attempt in range(max_retries):
            try:
                embeddings = embed_chunks_cohere(chunks)
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} embedding error for {file_path.name}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        if embeddings is None:
            print(f"Failed to get embeddings for {file_path.name} after multiple retries.")
            return None

        serialized_chunks = []
        langchain_documents = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_data = {
                "page_content": chunk.page_content,
                "metadata": {
                    **chunk.metadata,
                    "embedding": embedding.tolist(),
                    "embedding_model": "cohere-embed-english-v3.0",
                    "embedding_time": datetime.datetime.now().isoformat()
                }
            }
            serialized_chunks.append(chunk_data)
            # Create LangChain Document for Pinecone
            langchain_documents.append(Document(page_content=chunk.page_content, metadata=chunk.metadata))

        return {
            "file": str(file_path),
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "chunks": serialized_chunks,
            "langchain_documents": langchain_documents
        }
    except Exception as e:
        print(f"Failed processing {file_path.name}: {str(e)}")
        return None

def process_all_pdfs(pdf_files: List[Path]) -> List[Dict[str, Any]]:
    results = []
    for pdf_file in pdf_files:
        result = process_pdf(pdf_file)
        results.append(result)
    return results

def main():
    pdf_files = list(set(Path("guides/").rglob("*.[pP][dD][fF]")))
    print(f"Found {len(pdf_files)} PDF files to process")

    results = process_all_pdfs(pdf_files)

    successful = [r for r in results if isinstance(r, dict)]
    failed = len(results) - len(successful)

    total_embedded = sum(len(res["chunks"]) for res in successful)

    print(f"\nProcessing complete:")
    print(f"- Success: {len(successful)} files")
    print(f"- Failed: {failed} files")
    print(f"- Total chunks embedded: {total_embedded}")

    # Initialize Pinecone and Vector Store
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)

    index = pc.Index(PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)

    # Add documents to Pinecone
    for result in successful:
        if result and "langchain_documents" in result:
            documents = result["langchain_documents"]
            uuids = [str(uuid4()) for _ in range(len(documents))]
            vector_store.add_documents(documents=documents, ids=uuids)
        else:
            print(f"Skipping adding documents for a failed file: {result['file'] if result else 'Unknown'}")

    print("Documents added to Pinecone.")

    if 'COHERE_API_KEY' in os.environ:
        del os.environ['COHERE_API_KEY']
    if 'PINECONE_API_KEY' in os.environ:
        del os.environ['PINECONE_API_KEY']

if __name__ == "__main__":
    main()