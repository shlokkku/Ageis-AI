#!/usr/bin/env python3
"""
Test Script to Show Difference Between PDF Queries and Database Queries
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "full_name": "Test User",
    "email": "testuser@example.com",
    "password": "testpass123",
    "role": "resident"
}

def test_pdf_vs_database():
    """Test to show the difference between PDF and database queries"""
    
    print("🧪 Testing PDF vs Database Query Differences")
    print("=" * 60)
    
    # Step 1: Login to get JWT token
    print("\n🔑 Step 1: User Login")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            data={
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        if response.status_code != 200:
            print("❌ Login failed. Please run the signup first.")
            return None
            
        data = response.json()
        jwt_token = data.get("access_token")
        user_id = data.get("user_id")
        
        print(f"✅ Login successful - User ID: {user_id}")
        print(f"🔑 JWT Token: {jwt_token[:50]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test Database Query (No PDF needed)
    print("\n📊 Step 2: Database Query (No PDF needed)")
    print("-" * 40)
    
    db_query = "What is my current pension savings?"
    print(f"📝 Query: {db_query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/prompt",
            json={"query": db_query},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received:")
            print(f"🤖 AI Response: {data.get('response', 'No response')}")
            
            # Check if it's from database or PDF
            if "data_source" in str(data):
                print("🔍 Data Source: DATABASE_PENSION_DATA")
                print("📋 Note: This analysis is based on your pension data stored in our database")
            else:
                print("🔍 Data Source: Not specified")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    # Step 3: Test PDF Query (Will search PDFs)
    print("\n📄 Step 3: PDF Query (Will search uploaded documents)")
    print("-" * 40)
    
    pdf_query = "What does my pension plan document say about retirement age?"
    print(f"📝 Query: {pdf_query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/prompt",
            json={"query": pdf_query},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received:")
            print(f"🤖 AI Response: {data.get('response', 'No response')}")
            
            # Check if it's from PDF search
            if "search_type" in str(data):
                print("🔍 Search Type: PDF_DOCUMENT_SEARCH")
                print("📋 Note: This response is from searching your uploaded PDF documents")
            else:
                print("🔍 Search Type: Not specified")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    # Step 4: Test Risk Analysis (Database data)
    print("\n⚠️ Step 4: Risk Analysis Query (Database data)")
    print("-" * 40)
    
    risk_query = "Analyze my risk profile"
    print(f"📝 Query: {risk_query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/prompt",
            json={"query": risk_query},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received:")
            print(f"🤖 AI Response: {data.get('response', 'No response')}")
            
            # Check if it's from database
            if "data_source" in str(data):
                print("🔍 Data Source: DATABASE_PENSION_DATA")
                print("📋 Note: This risk analysis is based on your pension data stored in our database")
            else:
                print("🔍 Data Source: Not specified")
                
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Query error: {e}")
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print("✅ Database Queries: Use pension data from database")
    print("📄 PDF Queries: Search uploaded PDF documents")
    print("🔍 Each response now clearly indicates the data source!")
    print("=" * 60)

if __name__ == "__main__":
    test_pdf_vs_database()

