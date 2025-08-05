import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Groq API for LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "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")
    
    # Pinecone for Vector Store
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "pcsk_45RcPZ_H7v5L1azm45BDJNHCrCs8NtvgZeq2xtpffgMuVc4vHykDbHjyxUzTmH9VzD8tL8")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_INDEX_NAME: str = "project"
    VECTOR_DIMENSION: int = 384  # all-MiniLM-L6-v2 embedding dimension
    
    # MongoDB for Document Storage
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://bajaj04:Strawhat04@cluster0.hyhyggi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    
    # Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # HuggingFace Model (FREE, no API key needed)
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

settings = Settings()
