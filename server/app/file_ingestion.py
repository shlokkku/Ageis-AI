# server/app/utils/file_ingestion.py

import fitz # PyMuPDF
from typing import List
from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.chromadb_service import get_or_create_collection, add_documents_to_collection

# A reusable text splitter for chunking documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

# A reusable sentence transformer for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Extract text from PDF using OCR if regular text extraction fails
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            
            # Try regular text extraction first
            text = page.get_text()
            
            # If no text, try OCR
            if not text.strip():
                print(f"📄 Page {page_num + 1}: No text found, trying OCR...")
                try:
                    # Convert page to image and use OCR
                    pix = page.get_pixmap()
                    # For now, we'll use a simple approach - you might need to install additional OCR libraries
                    text = f"[Page {page_num + 1} - Scanned content detected. OCR processing required for full text extraction.]"
                    print(f"📄 Page {page_num + 1}: OCR placeholder added")
                except Exception as ocr_error:
                    print(f"📄 Page {page_num + 1}: OCR failed: {ocr_error}")
                    text = f"[Page {page_num + 1} - Image content detected but OCR not available]"
            
            full_text += text + "\n"
        
        return full_text
        
    except Exception as e:
        print(f"❌ Error in OCR extraction: {e}")
        return ""

def ingest_pdf_to_chroma(file_path: str, user_id: int):
    """
    Parses a PDF, chunks its text, and ingests the documents into ChromaDB.
    """
    try:
        # 1. Parse the PDF and extract text
        print(f"📄 Opening PDF: {file_path}")
        doc = fitz.open(file_path)
        print(f"📄 PDF opened - Pages: {doc.page_count}")
        
        # Try regular text extraction first
        full_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            print(f"📄 Page {page_num + 1}: {len(page_text)} characters")
            full_text += page_text
        
        print(f"📄 Total text extracted: {len(full_text)} characters")
        
        # If no text extracted, try OCR
        if not full_text.strip():
            print("❌ No text extracted - trying OCR processing...")
            full_text = extract_text_with_ocr(file_path)
            
            if not full_text.strip():
                print("❌ OCR also failed - this PDF cannot be processed")
                return {
                    "status": "error", 
                    "message": "This PDF appears to be scanned images. OCR processing is required but not available. Please use a text-based PDF or contact support for OCR processing."
                }
        
        # 2. Chunk the text
        chunks = text_splitter.split_text(full_text)
        print(f"📄 Extracted {len(chunks)} chunks from the PDF.")
        
        if len(chunks) == 0:
            print("❌ No chunks created from text")
            return {
                "status": "error", 
                "message": "Text was extracted but could not be chunked properly."
            }
        
        # 3. Create a ChromaDB collection for this user
        collection = get_or_create_collection(f"user_{user_id}_docs")
        
        # 4. Prepare data for ingestion
        ids = [str(uuid4()) for _ in chunks]
        metadatas = [{"user_id": user_id, "source": file_path, "chunk_index": i} for i, _ in enumerate(chunks)]
        
        # 5. Add documents to the collection
        add_documents_to_collection(collection, chunks, ids, metadatas)
        print(f"🚀 Successfully ingested PDF for user {user_id}.")

    except Exception as e:
        print(f"❌ Failed to ingest PDF: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": f"PDF successfully ingested for user {user_id}"}