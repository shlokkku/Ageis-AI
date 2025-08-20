#!/usr/bin/env python3
"""
Simple PDF Search Test - Tests the core PDF search functionality
"""

import sys
import os
from pathlib import Path

def test_pdf_search_core():
    """Test the core PDF search functionality"""
    try:
        print("🧪 Testing Core PDF Search Functionality")
        print("=" * 50)
        
        # Add the server directory to Python path
        server_path = Path(__file__).parent / "server"
        sys.path.insert(0, str(server_path))
        
        # Test 1: Import the tools
        print("🔧 Step 1: Testing tool imports...")
        try:
            from app.tools.tools import (
                query_knowledge_base, 
                analyze_uploaded_document,
                knowledge_base_search,
                set_request_user_id
            )
            print("✅ Successfully imported PDF search tools")
        except ImportError as e:
            print(f"❌ Import Error: {e}")
            print("Make sure you're running this from the correct directory")
            return
        
        # Test 2: Test ChromaDB connection
        print("\n🔍 Step 2: Testing ChromaDB connection...")
        try:
            from app.chromadb_service import get_or_create_collection, query_collection
            
            # Test general collection
            print("Testing general pension knowledge collection...")
            general_collection = get_or_create_collection("pension_knowledge")
            print(f"✅ General collection: {general_collection}")
            
            # Test user document collection
            test_user_id = 99
            print(f"Testing user {test_user_id} document collection...")
            user_collection = get_or_create_collection(f"user_{test_user_id}_docs")
            print(f"✅ User collection: {user_collection}")
            
        except Exception as e:
            print(f"❌ ChromaDB Error: {e}")
            return
        
        # Test 3: Test PDF search tools
        print("\n🔍 Step 3: Testing PDF search tools...")
        try:
            # Set user context
            set_request_user_id(test_user_id)
            print(f"✅ Set user context for user {test_user_id}")
            
            # Test query_knowledge_base
            print("\n--- Testing query_knowledge_base ---")
            result1 = query_knowledge_base("What information is available in my documents?", test_user_id)
            print(f"✅ query_knowledge_base result: {result1}")
            
            # Test analyze_uploaded_document
            print("\n--- Testing analyze_uploaded_document ---")
            result2 = analyze_uploaded_document("What does my pension plan document say?", test_user_id)
            print(f"✅ analyze_uploaded_document result: {result2}")
            
            # Test knowledge_base_search
            print("\n--- Testing knowledge_base_search ---")
            result3 = knowledge_base_search("What information is in my uploaded documents?", test_user_id)
            print(f"✅ knowledge_base_search result: {result3}")
            
        except Exception as e:
            print(f"❌ Tool testing error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n🎉 Core PDF Search Test Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

def test_pdf_file_detection():
    """Test PDF file detection in current directory"""
    print("\n📄 PDF File Detection Test")
    print("=" * 30)
    
    # Check for PDF files
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF file(s):")
        for pdf_file in pdf_files:
            file_size = os.path.getsize(pdf_file)
            print(f"   📄 {pdf_file} ({file_size:,} bytes)")
    else:
        print("❌ No PDF files found in current directory")
        print("💡 Place a PDF file in this directory or provide a path")
    
    return pdf_files

if __name__ == "__main__":
    print("🚀 Starting Simple PDF Search Test...")
    
    # Test 1: PDF file detection
    pdf_files = test_pdf_file_detection()
    
    # Test 2: Core functionality
    if pdf_files:
        print(f"\n🎯 Testing with detected PDF: {pdf_files[0]}")
        test_pdf_search_core()
    else:
        print("\n⚠️ No PDF files found - testing core functionality only")
        test_pdf_search_core()
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")
