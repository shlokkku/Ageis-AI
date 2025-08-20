#!/usr/bin/env python3
"""
Test script to verify PDF search functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the server directory to Python path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

def test_pdf_search_tools():
    """Test the PDF search tools directly"""
    print("🔍 Testing PDF Search Tools...")
    
    try:
        # Import the tools
        from app.tools.tools import (
            query_knowledge_base, 
            analyze_uploaded_document,
            knowledge_base_search,
            set_request_user_id
        )
        
        print("✅ Successfully imported PDF search tools")
        
        # Test with a sample user ID
        test_user_id = 520
        test_query = "What is my pension plan?"
        
        print(f"\n🔍 Testing with user_id={test_user_id}, query='{test_query}'")
        
        # Set the user ID in context
        set_request_user_id(test_user_id)
        
        # Test 1: query_knowledge_base (PDF search)
        print("\n--- Test 1: query_knowledge_base ---")
        try:
            result1 = query_knowledge_base(test_query, test_user_id)
            print(f"✅ query_knowledge_base result: {json.dumps(result1, indent=2)}")
        except Exception as e:
            print(f"❌ query_knowledge_base error: {e}")
        
        # Test 2: analyze_uploaded_document
        print("\n--- Test 2: analyze_uploaded_document ---")
        try:
            result2 = analyze_uploaded_document(test_query, test_user_id)
            print(f"✅ analyze_uploaded_document result: {json.dumps(result2, indent=2)}")
        except Exception as e:
            print(f"❌ analyze_uploaded_document error: {e}")
        
        # Test 3: knowledge_base_search (enhanced)
        print("\n--- Test 3: knowledge_base_search ---")
        try:
            result3 = knowledge_base_search(test_query, test_user_id)
            print(f"✅ knowledge_base_search result: {json.dumps(result3, indent=2)}")
        except Exception as e:
            print(f"❌ knowledge_base_search error: {e}")
        
        print("\n🎉 PDF Search Tools Test Complete!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're running this from the correct directory")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

def test_chromadb_connection():
    """Test ChromaDB connection and collections"""
    print("\n🔍 Testing ChromaDB Connection...")
    
    try:
        from app.chromadb_service import get_or_create_collection, query_collection
        
        # Test general collection
        print("Testing general pension knowledge collection...")
        general_collection = get_or_create_collection("pension_knowledge")
        print(f"✅ General collection: {general_collection}")
        
        # Test user document collection
        test_user_id = 520
        print(f"Testing user {test_user_id} document collection...")
        user_collection = get_or_create_collection(f"user_{test_user_id}_docs")
        print(f"✅ User collection: {user_collection}")
        
        # Test a simple query
        test_query = "pension"
        print(f"Testing query: '{test_query}'")
        results = query_collection(general_collection, [test_query], n_results=1)
        print(f"✅ Query results: {results}")
        
    except Exception as e:
        print(f"❌ ChromaDB Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting PDF Search Tools Test...")
    print("=" * 50)
    
    # Test ChromaDB connection first
    test_chromadb_connection()
    
    # Test the tools
    test_pdf_search_tools()
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")
