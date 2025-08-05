#!/usr/bin/env python3
"""
Test script for the Insurance LLM Backend API
"""

import requests
import json
import time

def test_insurance_analysis_api():
    """Test the insurance analysis API endpoint"""
    
    print("🧪 Testing Insurance Analysis API")
    print("=" * 40)
    
    # Test data
    test_query = {
        "query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
    }
    
    try:
        # Test the analyze endpoint
        print("📡 Sending request to /analyze/ endpoint...")
        response = requests.post(
            "http://localhost:8000/analyze/",
            json=test_query,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response received successfully!")
            print(f"📊 Decision: {result['decision']['decision']}")
            print(f"💰 Amount: {result['decision']['amount']}")
            print(f"📝 Justification: {result['decision']['justification']}")
            print(f"🎯 Confidence: {result['decision']['confidence_score']}")
            print(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
            
            # Print extracted entities
            entities = result['extracted_entities']
            print(f"\n🔍 Extracted Entities:")
            print(f"   Age: {entities['age']}")
            print(f"   Gender: {entities['gender']}")
            print(f"   Condition: {entities['condition']}")
            print(f"   Location: {entities['location']}")
            print(f"   Policy Duration: {entities['policy_duration']}")
            
            # Print matched clauses
            print(f"\n📋 Matched Clauses ({len(result['matched_clauses'])}):")
            for i, clause in enumerate(result['matched_clauses'][:3], 1):
                print(f"   {i}. {clause['clause_title']} (Score: {clause['relevance_score']:.2f})")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_health_check():
    """Test the health check endpoint"""
    
    print("\n🏥 Testing Health Check API")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health/")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check successful!")
            print(f"📊 Status: {result['status']}")
            print(f"🗄️  Vector DB: {result['vector_database']['total_vectors']} vectors")
            print(f"🔧 Services: {', '.join(result['services'].keys())}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error in health check: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Test health check first
    test_health_check()
    
    # Test insurance analysis
    test_insurance_analysis_api()
    
    print("\n🎉 API tests completed!") 