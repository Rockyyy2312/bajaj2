from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from app.models.request_response import HackRXRequest, HackRXResponse, Answer
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store_service
from app.services.llm_service import llm_service
from app.database.mongodb import mongodb_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up the application...")
    await mongodb_service.connect()
    await vector_store_service.initialize()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down the application...")
    await mongodb_service.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="HackRX Insurance AI API",
    description="AI-powered insurance policy analysis system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HackRX Insurance AI API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hackrx-insurance-ai"}

@app.post("/api/v1/hackrx/run", response_model=HackRXResponse)
async def process_insurance_document(request: HackRXRequest):
    """
    Main endpoint for processing insurance policy documents
    """
    try:

        logger.info(f"Processing document from URL: {request.blob_url}")
        
        # Step 1: Process the document
        document_data = await document_processor.process_document(request.blob_url)
        logger.info("Document processing completed")
        
        # Step 2: Create document chunks and store in vector database
        documents = vector_store_service.split_documents(
            text=document_data["full_text"],
            metadata={
                "source_url": request.blob_url,
                "document_type": "insurance_policy",
                "total_pages": document_data["total_pages"]
            }
        )
        
        # Add to vector store
        vector_ids = await vector_store_service.add_documents(documents)
        logger.info(f"Added {len(vector_ids)} document chunks to vector store")
        
        # Step 3: Store document chunks in MongoDB
        chunks_data = []
        for i, doc in enumerate(documents):
            chunks_data.append({
                "vector_id": vector_ids[i] if i < len(vector_ids) else None,
                "content": doc.page_content,
                "metadata": doc.metadata,
                "source_url": request.blob_url
            })
        
        await mongodb_service.store_document_chunks(chunks_data)
        logger.info("Document chunks stored in MongoDB")
        
        # Step 4: Generate answers using LLM
        answers_data = await llm_service.generate_answers(document_data["full_text"])
        logger.info(f"Generated {len(answers_data)} answers")
        
        # Step 5: Format response
        answers = [Answer(**answer) for answer in answers_data]
        response = HackRXResponse(answers=answers)
        
        logger.info("Successfully processed insurance document")
        return response
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
if _name_ == "_main_":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
)
