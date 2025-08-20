#!/usr/bin/env python3
"""
Debug AI Response Script
Examines the full response structure from AI queries to identify missing indicators
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "one@gmail.com",
    "password": "shlok160404"
}

def debug_ai_response():
    """Debug the AI response structure"""
    print("🔍 Debugging AI Response Structure")
    print("=" * 60)
    
    # Step 1: Login
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
            print(f"❌ Login failed: {response.status_code}")
            return
        
        data = response.json()
        jwt_token = data.get("access_token")
        user_id = data.get("user_id")
        print(f"✅ Login successful - User ID: {user_id}")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test Database Query
    print("\n📊 Step 2: Test Database Query")
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    query = "What is my current pension savings?"
    print(f"📝 Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/prompt",
            json={"query": query},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Database query successful")
            print("\n🔍 FULL RESPONSE STRUCTURE:")
            print(json.dumps(data, indent=2))
            
            # Check for specific fields
            print("\n🔍 FIELD ANALYSIS:")
            print(f"Response field exists: {'response' in data}")
            if 'response' in data:
                print(f"Response content: {data['response'][:200]}...")
            
            print(f"Data source in response: {'data_source' in str(data['response'])}")
            print(f"Data source in metadata: {'data_source' in str(data.get('metadata', {}))}")
            print(f"Data source in chart_data: {'data_source' in str(data.get('chart_data', {}))}")
            
            # Check if data_source is in the workflow result
            if 'metadata' in data and 'workflow_result' in data['metadata']:
                workflow_result = data['metadata']['workflow_result']
                print(f"\n🔍 WORKFLOW RESULT ANALYSIS:")
                print(f"Workflow result type: {type(workflow_result)}")
                if isinstance(workflow_result, dict):
                    print(f"Data source in workflow: {'data_source' in str(workflow_result)}")
                    print(f"Search type in workflow: {'search_type' in str(workflow_result)}")
            
        else:
            print(f"❌ Database query failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Database query error: {e}")
    
    # Step 3: Test PDF Query
    print("\n📄 Step 3: Test PDF Query")
    query = "What does my uploaded pension plan document say about retirement age?"
    print(f"📝 Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/prompt",
            json={"query": query},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PDF query successful")
            print("\n🔍 FULL RESPONSE STRUCTURE:")
            print(json.dumps(data, indent=2))
            
            # Check for specific fields
            print("\n🔍 FIELD ANALYSIS:")
            print(f"Response field exists: {'response' in data}")
            if 'response' in data:
                print(f"Response content: {data['response'][:200]}...")
            
            print(f"Search type in response: {'search_type' in str(data['response'])}")
            print(f"Search type in metadata: {'search_type' in str(data.get('metadata', {}))}")
            print(f"Search type in chart_data: {'search_type' in str(data.get('chart_data', {}))}")
            
            # Check if search_type is in the workflow result
            if 'metadata' in data and 'workflow_result' in data['metadata']:
                workflow_result = data['metadata']['workflow_result']
                print(f"\n🔍 WORKFLOW RESULT ANALYSIS:")
                print(f"Workflow result type: {type(workflow_result)}")
                if isinstance(workflow_result, dict):
                    print(f"Search type in workflow: {'search_type' in str(workflow_result)}")
                    print(f"PDF status in workflow: {'pdf_status' in str(workflow_result)}")
            
        else:
            print(f"❌ PDF query failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ PDF query error: {e}")

if __name__ == "__main__":
    debug_ai_response()

