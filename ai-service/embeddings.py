import os
import functools
from langchain_huggingface import HuggingFaceEmbeddings

@functools.lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Initializes and returns the HuggingFace embedding model as a Singleton.
    Uses lru_cache to ensure the model is loaded only once per application lifecycle.
    """
    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    print(f"Loading embedding model: {model_name}...")
    
    # Initialize the embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )
    
    return embeddings

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    print("Testing HuggingFace Embeddings initialization...")
    model = get_embedding_model()
    
    # Test an embedding generation
    sample_text = "This is a test document."
    print(f"\nGenerating embedding for text: '{sample_text}'")
    vector = model.embed_query(sample_text)
    
    print(f"Successfully generated embedding.")
    print(f"Vector Dimensionality: {len(vector)}")
    print(f"Vector Sample (first 5 elements): {vector[:5]}")
