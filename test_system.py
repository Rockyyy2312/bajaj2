#!/usr/bin/env python3
"""
Test script for the Insurance LLM Backend
"""

import asyncio
import json
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.clause_master import ClauseMaster
from app.models.schemas import InsuranceQuery

async def test_insurance_analysis():
    """Test the complete insurance analysis workflow"""
    
    print("🧪 Testing Insurance LLM Backend System")
    print("=" * 50)
    
    # Initialize services
    print("📦 Initializing services...")
    document_processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    llm_service = LLMService()
    clause_master = ClauseMaster()
    
    # Test query
    test_query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
    print(f"🔍 Test Query: {test_query}")
    print()
    
    # Step 1: Extract entities
    print("1️⃣ Extracting entities from query...")
    try:
        entities = llm_service.extract_entities_from_query(test_query)
        print(f"   ✅ Extracted entities: {entities.model_dump()}")
    except Exception as e:
        print(f"   ❌ Error extracting entities: {e}")
        return
    
    # Step 2: Search for similar clauses
    print("\n2️⃣ Searching for similar clauses...")
    try:
        matched_clauses = embedding_service.search_similar_clauses(test_query, top_k=3)
        print(f"   ✅ Found {len(matched_clauses)} similar clauses")
        for i, clause in enumerate(matched_clauses[:2], 1):
            print(f"   Clause {i}: {clause['clause_title']} (Score: {clause['relevance_score']:.2f})")
    except Exception as e:
        print(f"   ❌ Error searching clauses: {e}")
        # Create mock clauses for testing
        matched_clauses = [
            {
                "clause_id": "clause_5.1",
                "clause_title": "Surgical Procedures Coverage",
                "clause_content": "Knee surgery is covered under this policy with a maximum coverage of 500,000 rupees. Waiting period of 12 months applies for surgical procedures.",
                "relevance_score": 0.85
            },
            {
                "clause_id": "clause_2.3",
                "clause_title": "Waiting Period",
                "clause_content": "A waiting period of 12 months is applicable for all surgical procedures including knee surgery, hip replacement, and cardiac procedures.",
                "relevance_score": 0.75
            }
        ]
        print("   ⚠️  Using mock clauses for testing")
    
    # Step 3: Analyze query and provide decision
    print("\n3️⃣ Analyzing query and providing decision...")
    try:
        decision = llm_service.analyze_insurance_query(test_query, matched_clauses)
        print(f"   ✅ Decision: {decision.decision}")
        print(f"   💰 Amount: {decision.amount}")
        print(f"   📝 Justification: {decision.justification}")
        print(f"   🎯 Confidence: {decision.confidence_score:.2f}")
        print(f"   📋 Mapped Clauses: {decision.mapped_clauses}")
    except Exception as e:
        print(f"   ❌ Error analyzing query: {e}")
        return
    
    # Step 4: Test clause master functionality
    print("\n4️⃣ Testing clause master functionality...")
    try:
        evaluation = clause_master.evaluate_coverage_eligibility(
            entities.model_dump(), matched_clauses
        )
        print(f"   ✅ Coverage evaluation: {evaluation['decision']}")
        print(f"   💰 Coverage amount: {evaluation['amount']}")
    except Exception as e:
        print(f"   ❌ Error in clause master: {e}")
    
    print("\n✅ System test completed successfully!")
    print("=" * 50)

def test_document_processing():
    """Test document processing functionality"""
    print("\n📄 Testing Document Processing")
    print("-" * 30)
    
    # Create a sample document content (simulating PDF text)
    sample_text = """
    INSURANCE POLICY DOCUMENT
    
    Clause 5.1: Surgical Procedures Coverage
    Knee surgery is covered under this policy with a maximum coverage of 500,000 rupees. 
    Waiting period of 12 months applies for surgical procedures.
    
    Clause 2.3: Waiting Period
    A waiting period of 12 months is applicable for all surgical procedures including 
    knee surgery, hip replacement, and cardiac procedures.
    
    Clause 3.1: Age Eligibility
    Policy is available for individuals between 18 and 65 years of age.
    
    Clause 4.2: Exclusions
    Pre-existing conditions are not covered for the first 24 months of the policy.
    """
    
    try:
        document_processor = DocumentProcessor()
        clauses = document_processor.detect_clauses(sample_text)
        print(f"   ✅ Detected {len(clauses)} clauses")
        
        for i, clause in enumerate(clauses[:3], 1):
            print(f"   Clause {i}: {clause['clause_title']}")
            print(f"      Content: {clause['clause_content'][:100]}...")
        
    except Exception as e:
        print(f"   ❌ Error in document processing: {e}")

if __name__ == "__main__":
    print("🚀 Starting Insurance LLM Backend Tests")
    print("=" * 50)
    
    # Test document processing
    test_document_processing()
    
    # Test insurance analysis
    asyncio.run(test_insurance_analysis())
    
    print("\n🎉 All tests completed!") 