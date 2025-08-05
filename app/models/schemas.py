from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DecisionType(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    PARTIAL = "partial"

class InsuranceQuery(BaseModel):
    """Natural language insurance query from user"""
    query: str = Field(..., description="Natural language query about insurance coverage")
    
class ExtractedEntities(BaseModel):
    """Extracted entities from the insurance query"""
    age: Optional[int] = Field(None, description="Age of the person")
    gender: Optional[str] = Field(None, description="Gender (male/female)")
    condition: Optional[str] = Field(None, description="Medical condition or procedure")
    location: Optional[str] = Field(None, description="Location of treatment")
    policy_duration: Optional[str] = Field(None, description="Policy duration or age")
    coverage_type: Optional[str] = Field(None, description="Type of coverage needed")
    
class ClauseMatch(BaseModel):
    """Matched clause from insurance documents"""
    clause_id: str = Field(..., description="Unique identifier for the clause")
    clause_title: str = Field(..., description="Title or name of the clause")
    clause_content: str = Field(..., description="Content of the clause")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    
class InsuranceDecision(BaseModel):
    """Final insurance decision response"""
    decision: DecisionType = Field(..., description="Final decision on coverage")
    amount: Optional[float] = Field(None, description="Coverage amount in currency")
    justification: str = Field(..., description="Detailed justification for the decision")
    mapped_clauses: List[str] = Field(..., description="List of relevant clause IDs")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the decision")
    waiting_period_info: Optional[str] = Field(None, description="Information about waiting periods")
    exclusions: Optional[List[str]] = Field(None, description="List of applicable exclusions")
    
class QueryAnalysisResponse(BaseModel):
    """Complete response for insurance query analysis"""
    query: str = Field(..., description="Original query")
    extracted_entities: ExtractedEntities = Field(..., description="Extracted entities from query")
    matched_clauses: List[ClauseMatch] = Field(..., description="Relevant clauses found")
    decision: InsuranceDecision = Field(..., description="Final insurance decision")
    processing_time: float = Field(..., description="Processing time in seconds")
    
class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    document_id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    pages_processed: int = Field(..., description="Number of pages processed")
    clauses_extracted: int = Field(..., description="Number of clauses extracted")
    status: str = Field(..., description="Processing status")
    
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    error_code: Optional[str] = Field(None, description="Error code for debugging")
