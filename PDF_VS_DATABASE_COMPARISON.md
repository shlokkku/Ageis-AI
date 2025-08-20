# 🔍 PDF vs Database Query Comparison

## 📊 **How to Tell the Difference in Postman Responses**

The `/prompt` endpoint handles both types of queries, but now you can clearly see which data source was used!

---

## 🎯 **Database Queries (No PDFs Needed)**

### **Query Examples:**
- "What is my current pension savings?"
- "Analyze my risk profile"
- "Check for fraud in my pension"
- "What will my pension be at retirement?"

### **Response Indicators:**
```json
{
  "response": "Your current savings are ₹2,500,000...",
  "user_id": 123,
  "data_source": "DATABASE_PENSION_DATA",           // 🔑 KEY INDICATOR
  "note": "This analysis is based on your pension data stored in our database, not from uploaded documents."
}
```

**🔍 Look for:** `"data_source": "DATABASE_PENSION_DATA"`

---

## 📄 **PDF Queries (Requires Uploaded Documents)**

### **Query Examples:**
- "What does my pension plan document say about retirement age?"
- "What are the contribution limits in my uploaded plan?"
- "What does my document say about investment options?"

### **Response Indicators (No PDFs Found):**
```json
{
  "response": "I searched your uploaded documents but found no relevant information...",
  "user_id": 123,
  "search_type": "PDF_DOCUMENT_SEARCH",             // 🔑 KEY INDICATOR
  "pdf_status": "NO_PDFS_FOUND",                   // 🔑 KEY INDICATOR
  "note": "This response is from searching your uploaded PDF documents. No relevant documents were found for your query."
}
```

**🔍 Look for:** 
- `"search_type": "PDF_DOCUMENT_SEARCH"`
- `"pdf_status": "NO_PDFS_FOUND"`

### **Response Indicators (PDFs Found):**
```json
{
  "response": "Based on your uploaded pension plan document, the contribution limits are...",
  "user_id": 123,
  "search_type": "PDF_DOCUMENT_SEARCH",             // 🔑 KEY INDICATOR
  "pdf_status": "PDFS_FOUND_AND_SEARCHED",         // 🔑 KEY INDICATOR
  "note": "This response is based on content extracted from your uploaded PDF documents."
}
```

**🔍 Look for:**
- `"search_type": "PDF_DOCUMENT_SEARCH"`
- `"pdf_status": "PDFS_FOUND_AND_SEARCHED"`

---

## 📋 **Quick Reference Table**

| Query Type | Look For | Meaning |
|------------|----------|---------|
| **Database Query** | `"data_source": "DATABASE_PENSION_DATA"` | Used your stored pension data |
| **PDF Search (No PDFs)** | `"search_type": "PDF_DOCUMENT_SEARCH"` + `"pdf_status": "NO_PDFS_FOUND"` | Searched PDFs but found none |
| **PDF Search (Found PDFs)** | `"search_type": "PDF_DOCUMENT_SEARCH"` + `"pdf_status": "PDFS_FOUND_AND_SEARCHED"` | Found and searched PDFs |

---

## 🧪 **Test in Postman**

### **Step 1: Test Database Query**
```http
POST {{base_url}}/prompt
{
  "query": "What is my current pension savings?"
}
```
**Expected:** `"data_source": "DATABASE_PENSION_DATA"`

### **Step 2: Test PDF Query**
```http
POST {{base_url}}/prompt
{
  "query": "What does my pension plan document say about retirement age?"
}
```
**Expected:** `"search_type": "PDF_DOCUMENT_SEARCH"` + `"pdf_status": "NO_PDFS_FOUND"`

### **Step 3: Upload PDF and Test Again**
```http
POST {{base_url}}/upload_pdf
# Upload a PDF file
```
Then repeat Step 2 - you should see `"pdf_status": "PDFS_FOUND_AND_SEARCHED"`

---

## 🎉 **Summary**

✅ **Database Queries:** Always work, use stored pension data  
✅ **PDF Queries:** Work with or without PDFs, clearly indicate status  
✅ **Clear Indicators:** Each response shows exactly what data source was used  
✅ **No Confusion:** You'll always know if it used PDFs or database data!  

**Happy Testing! 🧪✨**
