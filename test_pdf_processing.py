#!/usr/bin/env python3
"""
Test PDF Processing and ChromaDB
"""

import os
import sys
sys.path.append('server')

from app.chromadb_service import get_or_create_collection, query_collection
from app.file_ingestion import ingest_pdf_to_chroma

def test_chromadb():
    """Test ChromaDB functionality"""
    print("🧪 Testing ChromaDB Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Create a test collection
        print("1. Testing collection creation...")
        test_collection = get_or_create_collection("test_collection")
        print(f"✅ Collection created: {test_collection.name}")
        
        # Test 2: Add test documents
        print("2. Testing document addition...")
        test_docs = ["This is a test document about pensions", "Another test document about retirement"]
        test_ids = ["doc1", "doc2"]
        test_metadata = [{"source": "test", "user_id": 999}, {"source": "test", "user_id": 999}]
        
        test_collection.add(
            documents=test_docs,
            ids=test_ids,
            metadatas=test_metadata
        )
        print("✅ Test documents added")
        
        # Test 3: Query the collection
        print("3. Testing document query...")
        results = query_collection(test_collection, ["pension"], n_results=2)
        print(f"✅ Query successful: {len(results['documents'])} results found")
        
        # Test 4: Check user-specific collection
        print("4. Testing user-specific collection...")
        user_collection = get_or_create_collection("user_520_docs")
        print(f"✅ User collection exists: {user_collection.name}")
        
        # Test 5: Check if user collection has documents
        try:
            user_results = query_collection(user_collection, ["pension"], n_results=1)
            if user_results and user_results['documents']:
                print(f"✅ User collection has {len(user_results['documents'])} documents")
            else:
                print("⚠️ User collection exists but has no documents")
        except Exception as e:
            print(f"❌ Error querying user collection: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

def test_pdf_ingestion():
    """Test PDF ingestion"""
    print("\n📄 Testing PDF Ingestion")
    print("=" * 50)
    
    # Check if test PDF exists
    test_pdf_path = "Handbook_on_Family_Pension.pdf"
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF not found: {test_pdf_path}")
        return False
    
    try:
        print(f"1. Testing PDF ingestion for: {test_pdf_path}")
        result = ingest_pdf_to_chroma(test_pdf_path, user_id=520)
        
        if result["status"] == "success":
            print("✅ PDF ingestion successful")
            return True
        else:
            print(f"❌ PDF ingestion failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ PDF ingestion error: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 PDF Processing Debug Test")
    print("=" * 60)
    
    # Test ChromaDB
    chroma_success = test_chromadb()
    
    # Test PDF ingestion
    pdf_success = test_pdf_ingestion()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"ChromaDB: {'✅ PASS' if chroma_success else '❌ FAIL'}")
    print(f"PDF Ingestion: {'✅ PASS' if pdf_success else '❌ FAIL'}")
    
    if not chroma_success:
        print("\n🔧 ChromaDB Issues - Check:")
        print("1. Is sentence-transformers installed? (pip install sentence-transformers)")
        print("2. Are there any import errors in the console?")
    
    if not pdf_success:
        print("\n🔧 PDF Ingestion Issues - Check:")
        print("1. Is PyMuPDF installed? (pip install PyMuPDF)")
        print("2. Are there any file processing errors?")
    
    if chroma_success and pdf_success:
        print("\n🎉 All tests passed! The issue might be in the workflow routing.")

if __name__ == "__main__":
    main()
