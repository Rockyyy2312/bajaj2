import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_environment():
    """Validate required environment variables"""
    from app.utils.config import settings
    
    required_vars = {
        "GROQ_API_KEY": settings.GROQ_API_KEY,
        "PINECONE_API_KEY": settings.PINECONE_API_KEY,
        "MONGODB_URL": settings.MONGODB_URL,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    logger.info("Environment validation successful")

def format_documents_for_prompt(docs: List[Dict[str, Any]]) -> str:
    """Format documents for LLM prompt"""
    formatted_docs = []
    for i, doc in enumerate(docs, 1):
        content = doc.get('page_content', doc.get('content', ''))
        formatted_docs.append(f"Document {i}:\n{content}\n")
    
    return "\n".join(formatted_docs)
