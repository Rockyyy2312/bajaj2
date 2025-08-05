import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from app.utils.config import settings
from app.models.schemas import ExtractedEntities, InsuranceDecision, ClauseMatch

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

class LLMService:
    """Handle LLM interactions for insurance query processing"""
    
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model_name="meta-llama/llama-4-scout-17b-16e-instruct"  # or "mixtral-8x7b-32768"
        )
    
    def extract_entities_from_query(self, query: str) -> ExtractedEntities:
        """Extract entities from insurance query using LLM"""
        system_prompt = """You are an insurance expert. Extract key entities from the user's insurance query.
        
        Extract the following entities:
        - age: numeric age of the person
        - gender: male/female
        - condition: medical condition or procedure mentioned
        - location: city or location mentioned
        - policy_duration: policy age or duration mentioned
        - coverage_type: type of coverage needed
        
        Return only a JSON object with these fields. If a field is not found, use null."""
        
        user_prompt = f"Extract entities from this insurance query: {query}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            try:
                entities_dict = json.loads(response.content)
                return ExtractedEntities(**entities_dict)
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON, using fallback extraction")
                return self._fallback_entity_extraction(query)
                
        except Exception as e:
            logger.error(f"Error extracting entities with LLM: {e}")
            return self._fallback_entity_extraction(query)
    
    def _fallback_entity_extraction(self, query: str) -> ExtractedEntities:
        """Fallback entity extraction using simple regex patterns"""
        import re
        
        entities = {}
        
        # Age extraction
        age_match = re.search(r'(\d+)[\s-]*(?:year|yr)s?[\s-]*old', query, re.IGNORECASE)
        if age_match:
            entities["age"] = int(age_match.group(1))
        
        # Gender extraction
        gender_match = re.search(r'\b(male|female|man|woman)\b', query, re.IGNORECASE)
        if gender_match:
            entities["gender"] = gender_match.group(1).lower()
        
        # Medical condition
        medical_keywords = ["surgery", "operation", "knee", "hip", "heart", "cancer", "diabetes"]
        for keyword in medical_keywords:
            if keyword.lower() in query.lower():
                entities["condition"] = keyword
                break
        
        # Location
        locations = ["Mumbai", "Delhi", "Pune", "Bangalore", "Chennai", "Kolkata"]
        for location in locations:
            if location.lower() in query.lower():
                entities["location"] = location
                break
        
        # Policy duration
        duration_match = re.search(r'(\d+)[\s-]*(?:month|year|yr)s?[\s-]*(?:old|policy)', query, re.IGNORECASE)
        if duration_match:
            entities["policy_duration"] = duration_match.group(1)
        
        return ExtractedEntities(**entities)
    
    def analyze_insurance_query(self, query: str, matched_clauses: List[Dict[str, Any]]) -> InsuranceDecision:
        """Analyze insurance query and provide decision using LLM"""
        
        # Format clauses for prompt
        clauses_text = ""
        for i, clause in enumerate(matched_clauses, 1):
            clauses_text += f"Clause {i}: {clause['clause_title']}\n"
            clauses_text += f"Content: {clause['clause_content']}\n"
            clauses_text += f"Relevance: {clause.get('relevance_score', 0):.2f}\n\n"
        
        system_prompt = """You are an expert insurance analyst. Analyze the insurance query and relevant clauses to provide a decision.

        You must return a JSON response with the following structure:
        {
            "decision": "approved" or "rejected" or "pending" or "partial",
            "amount": numeric amount in currency (null if rejected),
            "justification": "detailed explanation of the decision",
            "mapped_clauses": ["list of relevant clause IDs"],
            "confidence_score": float between 0.0 and 1.0,
            "waiting_period_info": "information about waiting periods if applicable",
            "exclusions": ["list of applicable exclusions"]
        }
        
        Consider:
        - Age eligibility (18-65 years)
        - Waiting periods (3 months general, 12 months surgery, 24 months pre-existing)
        - Coverage limits from clauses
        - Exclusions and limitations
        - Policy duration requirements"""
        
        user_prompt = f"""Insurance Query: {query}

Relevant Clauses:
{clauses_text}

Provide your analysis and decision in JSON format."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm(messages)
            
            # Parse JSON response
            try:
                decision_dict = json.loads(response.content)
                return InsuranceDecision(**decision_dict)
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM decision as JSON, using fallback")
                return self._fallback_decision(query, matched_clauses)
                
        except Exception as e:
            logger.error(f"Error analyzing insurance query with LLM: {e}")
            return self._fallback_decision(query, matched_clauses)
    
    def _fallback_decision(self, query: str, matched_clauses: List[Dict[str, Any]]) -> InsuranceDecision:
        """Fallback decision logic when LLM fails"""
        from app.services.clause_master import ClauseMaster
        
        clause_master = ClauseMaster()
        
        # Extract entities
        entities = self._fallback_entity_extraction(query)
        entities_dict = entities.dict()
        
        # Evaluate coverage
        evaluation = clause_master.evaluate_coverage_eligibility(entities_dict, matched_clauses)
        
        # Map clause IDs
        mapped_clauses = [clause["clause_id"] for clause in matched_clauses[:3]]
        
        return InsuranceDecision(
            decision=evaluation["decision"],
            amount=evaluation["amount"],
            justification=evaluation["justification"],
            mapped_clauses=mapped_clauses,
            confidence_score=evaluation["confidence_score"],
            waiting_period_info=evaluation.get("waiting_period_info"),
            exclusions=evaluation.get("exclusions", [])
        )
    
    def process_pdf_and_get_feedback(self, pdf_content: bytes) -> str:
        """Process PDF and get feedback (legacy method)"""
        try:
            # This is a simple text extraction for basic feedback
            import fitz
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            return f"PDF processed successfully. Extracted {len(text)} characters of text."
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
    
    def generate_clause_summary(self, clauses: List[Dict[str, Any]]) -> str:
        """Generate a summary of clauses using LLM"""
        if not clauses:
            return "No clauses found in the document."
        
        clauses_text = ""
        for i, clause in enumerate(clauses[:5], 1):  # Limit to first 5 clauses
            clauses_text += f"{i}. {clause['clause_title']}: {clause['clause_content'][:200]}...\n\n"
        
        system_prompt = """You are an insurance expert. Provide a concise summary of the insurance clauses provided."""
        
        user_prompt = f"Summarize these insurance clauses:\n\n{clauses_text}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating clause summary: {e}")
            return f"Found {len(clauses)} clauses in the document."
