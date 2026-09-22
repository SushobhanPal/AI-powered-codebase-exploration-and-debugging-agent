import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from embeddings import get_embedding_model
from chunker import process_repository
from typing import List
from langchain_core.documents import Document

COLLECTION_NAME = "github_codebase"

def get_qdrant_client() -> QdrantClient:
    """
    Initializes and returns the raw Qdrant client.
    """
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_key = os.getenv("QDRANT_API_KEY")
    return QdrantClient(url=qdrant_url, api_key=api_key)

def get_vector_store() -> QdrantVectorStore:
    """
    Initializes and returns the LangChain QdrantVectorStore wrapper.
    Ensures the collection exists before returning.
    """
    client = get_qdrant_client()
    embeddings = get_embedding_model()
    
    # Check if collection exists, if not create it
    if not client.collection_exists(COLLECTION_NAME):
        # The sentence-transformers/all-MiniLM-L6-v2 model outputs 384 dimensions
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"Created new collection: {COLLECTION_NAME}")
        
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    return vector_store

def index_repository(url: str):
    """
    Fetches, chunks, and indexes an entire GitHub repository into Qdrant.
    """
    print(f"Starting indexing process for {url}...")
    documents = process_repository(url)
    
    if not documents:
        print("No documents found to index.")
        return
        
    print(f"Adding {len(documents)} chunks to Qdrant...")
    vector_store = get_vector_store()
    
    # LangChain handles the batching and embedding automatically here!
    vector_store.add_documents(documents)
    print("Indexing complete.")

def search_repository(query: str, repository_id: str, k: int = 5) -> List[Document]:
    """
    Performs a similarity search, filtering by repository_id.
    """
    from qdrant_client.http import models
    vector_store = get_vector_store()
    
    # Create a proper Qdrant Filter object
    qdrant_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.repository_id",
                match=models.MatchValue(value=repository_id),
            )
        ]
    )
    
    results = vector_store.similarity_search(
        query=query,
        k=k,
        filter=qdrant_filter
    )
    
    return results

def delete_repository(repository_id: str):
    """
    Deletes all vectors from the collection that match the given repository_id.
    """
    from qdrant_client.http import models
    client = get_qdrant_client()
    
    # Create the metadata filter
    qdrant_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.repository_id",
                match=models.MatchValue(value=repository_id),
            )
        ]
    )
    
    # Delete points matching the filter
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(filter=qdrant_filter)
    )
    print(f"Deleted vectors for repository: {repository_id}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    print("Testing Qdrant Database initialization...")
    try:
        vs = get_vector_store()
        print("Qdrant connection successful and collection verified.")
    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
