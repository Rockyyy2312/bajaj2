import time
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List

from app.models.schemas import (
    InsuranceQuery, QueryAnalysisResponse, DocumentUploadResponse, 
    ErrorResponse, ExtractedEntities, InsuranceDecision, ClauseMatch
)
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.clause_master import ClauseMaster
from app.utils.helpers import setup_logging

# Setup logging
setup_logging()

router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
embedding_service = EmbeddingService()
llm_service = LLMService()
clause_master = ClauseMaster()

@router.post("/analyze/", response_model=QueryAnalysisResponse)
async def analyze_insurance_query(query: InsuranceQuery):
    """
    Analyze an insurance query and provide coverage decision
    """
    start_time = time.time()
    
    try:
        # Step 1: Extract entities from query
        extracted_entities = llm_service.extract_entities_from_query(query.query)
        
        # Step 2: Search for relevant clauses using vector similarity
        matched_clauses = embedding_service.search_similar_clauses(
            query=query.query,
            top_k=5
        )
        
        # Step 3: Analyze query and provide decision using LLM
        decision = llm_service.analyze_insurance_query(query.query, matched_clauses)
        
        # Step 4: Calculate processing time
        processing_time = time.time() - start_time
        
        # Step 5: Format response
        response = QueryAnalysisResponse(
            query=query.query,
            extracted_entities=extracted_entities,
            matched_clauses=[
                ClauseMatch(
                    clause_id=clause["clause_id"],
                    clause_title=clause["clause_title"],
                    clause_content=clause["clause_content"],
                    relevance_score=clause["relevance_score"]
                )
                for clause in matched_clauses
            ],
            decision=decision,
            processing_time=processing_time
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing insurance query: {str(e)}"
        )

@router.post("/upload-document/", response_model=DocumentUploadResponse)
async def upload_insurance_document(file: UploadFile = File(...)):
    """
    Upload and process insurance document (PDF)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        document_id = str(uuid.uuid4())
        processed_doc = document_processor.process_document(file_content, file.filename)
        
        # Store clauses in vector database
        success = embedding_service.upsert_clauses(
            clauses=processed_doc["clauses"],
            document_id=document_id
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store document clauses in vector database"
            )
        
        # Generate clause summary
        clause_summary = llm_service.generate_clause_summary(processed_doc["clauses"])
        
        response = DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            pages_processed=processed_doc["total_pages"],
            clauses_extracted=processed_doc["total_clauses"],
            status="processed"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/health/")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check vector database
        stats = embedding_service.get_index_stats()
        
        return {
            "status": "healthy",
            "vector_database": {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0)
            },
            "services": {
                "document_processor": "operational",
                "embedding_service": "operational",
                "llm_service": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.delete("/documents/{document_id}/")
async def delete_document(document_id: str):
    """
    Delete a document and its associated clauses
    """
    try:
        success = embedding_service.delete_document_clauses(document_id)
        
        if success:
            return {"message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete document clauses"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@router.get("/documents/stats/")
async def get_document_stats():
    """
    Get statistics about stored documents and clauses
    """
    try:
        stats = embedding_service.get_index_stats()
        
        return {
            "total_vectors": stats.get("total_vector_count", 0),
            "index_dimension": stats.get("dimension", 0),
            "index_fullness": stats.get("index_fullness", 0),
            "namespaces": stats.get("namespaces", {})
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting document stats: {str(e)}"
        )

# Legacy endpoint for backward compatibility
@router.post("/analyze-pdf/")
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Legacy endpoint for PDF analysis
    """
    try:
        contents = await file.read()
        feedback = llm_service.process_pdf_and_get_feedback(contents)
        return {"result": feedback}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )
