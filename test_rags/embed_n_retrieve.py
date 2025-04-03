import asyncio
import numpy as np
import os
import aiohttp
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_cohere import CohereEmbeddings
from typing import List

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "tech-docs-index"

embeddings_model = CohereEmbeddings(
    model="embed-english-v3.0",
    truncate="END",
    max_retries=3,
)

async def embed_query_cohere(query: str, session: aiohttp.ClientSession) -> np.ndarray:
    try:
        async with session.post(
            "https://api.cohere.ai/v1/embed",
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "texts": [query],
                "model": "embed-english-v3.0",
                "input_type": "search_query",
                "truncate": "END"
            }
        ) as response:
            data = await response.json()
            return np.array(data['embeddings'][0])
    except Exception as e:
        print(f"Embedding error: {str(e)}")
        return np.zeros(1024)

async def retrieve_relevant_documents(query: str, top_k: int = 4) -> List[str]:
    """
    Retrieves relevant documents from Pinecone based on a query.

    Args:
        query: The query string.
        top_k: The number of top results to retrieve.

    Returns:
        A list of relevant document content strings.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)

    retrieved_docs = vector_store.similarity_search(query, k=top_k)

    return [doc.page_content for doc in retrieved_docs]

async def main_retriever(query_text: str):
    """
    Example usage of the retrieve_relevant_documents function.
    """
    relevant_docs = await retrieve_relevant_documents(query_text)
    for doc in relevant_docs:
        print(doc)
        print("---")

if __name__ == "__main__":
    query_text = "What was said about 'Creating Data Backup Discs'?"
    asyncio.run(main_retriever(query_text))