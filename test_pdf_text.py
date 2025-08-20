#!/usr/bin/env python3
"""
Test PDF Text Extraction
"""

import fitz  # PyMuPDF

def test_pdf_text():
    """Test if we can extract text from the PDF"""
    pdf_path = "Handbook_on_Family_Pension.pdf"
    
    print(f"🧪 Testing PDF Text Extraction: {pdf_path}")
    print("=" * 60)
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        print(f"✅ PDF opened successfully - Pages: {doc.page_count}")
        
        # Try to extract text from first few pages
        total_text = ""
        for page_num in range(min(3, doc.page_count)):
            page = doc.load_page(page_num)
            text = page.get_text()
            print(f"Page {page_num + 1}: {len(text)} characters")
            if text.strip():
                print(f"Sample text: {text[:100]}...")
                total_text += text
            else:
                print(f"Page {page_num + 1}: NO TEXT EXTRACTED")
        
        print(f"\nTotal text extracted: {len(total_text)} characters")
        
        if total_text.strip():
            print("✅ Text extraction successful")
            return True
        else:
            print("❌ No text extracted from PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return False

if __name__ == "__main__":
    test_pdf_text()
