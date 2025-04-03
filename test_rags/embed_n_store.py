import asyncio
import time
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from pathlib import Path
from typing import List, Dict, Any
import os
import datetime
import aiohttp
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

async def embed_chunks_cohere(chunks: List[Any], session: aiohttp.ClientSession) -> List[np.ndarray]:
    texts = [chunk.page_content for chunk in chunks]
    try:
        async with session.post(
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
        ) as response:
            data = await response.json()
            return np.array(data['embeddings'])
    except Exception as e:
        print(f"Embedding error: {str(e)}")
        return [np.zeros(1024) for _ in chunks]

async def process_pdf(file_path: Path, session: aiohttp.ClientSession) -> Dict[str, Any]:
    try:
        loader = PyPDFLoader(str(file_path))
        pages = [page async for page in loader.alazy_load()]
        chunks = []
        for page in pages:
            chunks.extend(text_splitter.split_documents([page]))

        max_retries = 3
        for attempt in range(max_retries):
            try:
                embeddings = await embed_chunks_cohere(chunks, session)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

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

async def process_all_pdfs(pdf_files: List[Path]) -> List[Dict[str, Any]]:
    connector = aiohttp.TCPConnector(limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector) as session:
        semaphore = asyncio.Semaphore(5)

        async def process_with_limit(file_path):
            async with semaphore:
                return await process_pdf(file_path, session)

        tasks = [process_with_limit(pdf_file) for pdf_file in pdf_files]
        return await asyncio.gather(*tasks, return_exceptions=True)

def main():
    pdf_files = list(set(Path("guides/").rglob("*.[pP][dD][fF]")))
    print(f"Found {len(pdf_files)} PDF files to process")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        results = loop.run_until_complete(process_all_pdfs(pdf_files))

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
            documents = result["langchain_documents"]
            uuids = [str(uuid4()) for _ in range(len(documents))]
            vector_store.add_documents(documents=documents, ids=uuids)

        print("Documents added to Pinecone.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        loop.close()
        if 'COHERE_API_KEY' in os.environ:
            del os.environ['COHERE_API_KEY']
        if 'PINECONE_API_KEY' in os.environ:
            del os.environ['PINECONE_API_KEY']

if __name__ == "__main__":
    main()
    
    