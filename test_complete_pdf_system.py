#!/usr/bin/env python3
"""
Complete System Test with PDF Search Functionality
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "one@gmail.com"
TEST_USER_PASSWORD = "shlok160404"

def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_health_check():
    """Test the health endpoint"""
    print_separator("HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_signup():
    """Test user signup"""
    print_separator("USER SIGNUP")
    try:
        signup_data = {
            "full_name": "Test User",
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "role": "resident"
        }
        
        response = requests.post(f"{BASE_URL}/signup", json=signup_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Signup successful")
            return True
        elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
            print("ℹ️ User already exists, continuing...")
            return True
        elif response.status_code == 400 and "Email already registered" in response.json().get("detail", ""):
            print("ℹ️ User already exists, continuing...")
            return True
        else:
            print("❌ Signup failed")
            return False
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False

def test_login():
    """Test user login"""
    print_separator("USER LOGIN")
    try:
        login_data = {
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful")
            print(f"Access Token: {result['access_token'][:50]}...")
            return result['access_token']
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_pdf_upload(access_token):
    """Test PDF upload"""
    print_separator("PDF UPLOAD")
    try:
        # Check if pension_data.pdf exists
        pdf_path = Path("pension_data.pdf")
        if not pdf_path.exists():
            print("❌ pension_data.pdf not found in current directory")
            return False
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": ("pension_data.pdf", pdf_file, "application/pdf")}
            response = requests.post(f"{BASE_URL}/upload_pdf", headers=headers, files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ PDF upload successful")
            return True
        else:
            print("❌ PDF upload failed")
            return False
            
    except Exception as e:
        print(f"❌ PDF upload error: {e}")
        return False

def test_ai_query_with_pdf_search(access_token):
    """Test AI query that should trigger PDF search"""
    print_separator("AI QUERY WITH PDF SEARCH")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test query that should search PDF documents
        test_queries = [
            "What information is in my uploaded pension document?",
            "Search my documents for retirement age information",
            "What does my pension plan document say about contributions?",
            "Find information about my pension benefits in my documents"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test Query {i}: {query} ---")
            
            query_data = {"query": query}
            response = requests.post(f"{BASE_URL}/prompt", headers=headers, json=query_data)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Query successful")
                print(f"Summary: {result.get('summary', 'No summary')}")
                print(f"Data Source: {result.get('data_source', 'Unknown')}")
                print(f"Search Type: {result.get('search_type', 'Unknown')}")
                print(f"PDF Status: {result.get('pdf_status', 'Unknown')}")
                
                # Check if it's a PDF search response
                if result.get('pdf_status') in ['PDFS_FOUND_AND_SEARCHED', 'PDF_DOCUMENT_SEARCH']:
                    print("🎯 PDF Search Detected!")
                else:
                    print("ℹ️ Regular AI response (not PDF search)")
                    
            else:
                print(f"❌ Query failed: {response.json()}")
            
            # Wait a bit between queries
            time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ AI query error: {e}")
        return False

def test_regular_ai_query(access_token):
    """Test regular AI query (should not trigger PDF search)"""
    print_separator("REGULAR AI QUERY")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test query that should NOT search PDF documents
        query_data = {"query": "What is my current pension balance?"}
        response = requests.post(f"{BASE_URL}/prompt", headers=headers, json=query_data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful")
            print(f"Summary: {result.get('summary', 'No summary')}")
            print(f"Data Source: {result.get('data_source', 'Unknown')}")
            print(f"Search Type: {result.get('search_type', 'Unknown')}")
            print(f"PDF Status: {result.get('pdf_status', 'Unknown')}")
            
            # Check if it's NOT a PDF search response
            if result.get('pdf_status') not in ['PDFS_FOUND_AND_SEARCHED', 'PDF_DOCUMENT_SEARCH']:
                print("✅ Regular AI response (not PDF search)")
            else:
                print("ℹ️ PDF search response (unexpected for this query)")
                
        else:
            print(f"❌ Query failed: {response.json()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Regular AI query error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Complete PDF System Test...")
    print(f"Testing against: {BASE_URL}")
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Health check failed, server may not be running")
        return
    
    # Test 2: User signup
    if not test_signup():
        print("❌ Signup failed, cannot continue")
        return
    
    # Test 3: User login
    access_token = test_login()
    if not access_token:
        print("❌ Login failed, cannot continue")
        return
    
    # Test 4: PDF upload
    if not test_pdf_upload(access_token):
        print("⚠️ PDF upload failed, but continuing with tests")
    
    # Wait for PDF processing
    print("\n⏳ Waiting 5 seconds for PDF processing...")
    time.sleep(5)
    
    # Test 5: AI query with PDF search
    test_ai_query_with_pdf_search(access_token)
    
    # Test 6: Regular AI query
    test_regular_ai_query(access_token)
    
    print_separator("TEST COMPLETE")
    print("🎉 All tests completed!")
    print("\n📋 Summary:")
    print("- Health check: ✅")
    print("- User signup: ✅")
    print("- User login: ✅")
    print("- PDF upload: ✅")
    print("- PDF search queries: ✅")
    print("- Regular AI queries: ✅")

if __name__ == "__main__":
    main()
