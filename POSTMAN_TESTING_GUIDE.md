# 🧪 Postman Testing Guide for Pension AI API

## 🚀 **Quick Start (No PDFs Required)**

You can test the complete system without uploading any PDFs! The system will work with existing database data and gracefully handle PDF queries.

---

## 📋 **Step-by-Step Testing**

### **Step 1: Start Your Server**
```bash
cd pension-AI-main/server
python -m uvicorn app.main:app --reload
```

### **Step 2: Import Postman Collection**
1. Open Postman
2. Import the `Pension_AI_API_Postman_Collection.json` file
3. Set environment variable: `base_url = http://localhost:8000`

---

## 🔑 **Test 1: Authentication Flow**

### **1.1 User Registration**
```http
POST {{base_url}}/signup
Content-Type: application/json

{
  "full_name": "Test User",
  "email": "testuser@example.com",
  "password": "testpass123",
  "role": "resident"
}
```

**Expected Response:**
```json
{
  "id": 123,
  "full_name": "Test User",
  "email": "testuser@example.com",
  "role": "resident"
}
```

### **1.2 User Login**
```http
POST {{base_url}}/login
Content-Type: application/x-www-form-urlencoded

username=testuser@example.com&password=testpass123
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": 123,
  "role": "resident",
  "full_name": "Test User"
}
```

**💡 Save the `access_token` for subsequent requests!**

---

## 🤖 **Test 2: AI Queries (No PDFs Needed)**

### **2.1 Basic Pension Data Query (Database Data)**
```http
POST {{base_url}}/prompt
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "query": "What is my current pension savings?"
}
```

**Expected Response:**
```json
{
  "response": "Based on your pension data, your current savings are ₹2,500,000...",
  "user_id": 123,
  "data_source": "DATABASE_PENSION_DATA",
  "note": "This analysis is based on your pension data stored in our database, not from uploaded documents."
}
```

**🔍 Key Indicator:** Look for `"data_source": "DATABASE_PENSION_DATA"` - this means it used your stored pension data!

### **2.2 Risk Analysis Query (Database Data)**
```http
POST {{base_url}}/prompt
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "query": "Analyze my risk profile"
}
```

**Expected Response:**
```json
{
  "response": "Based on your risk analysis: Your risk level is Medium...",
  "user_id": 123,
  "data_source": "DATABASE_PENSION_DATA",
  "note": "This risk analysis is based on your pension data stored in our database, not from uploaded documents."
}
```

**🔍 Key Indicator:** `"data_source": "DATABASE_PENSION_DATA"` confirms it used database data!

### **2.3 Fraud Detection Query (Database Data)**
```http
POST {{base_url}}/prompt
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "query": "Check for any suspicious activity in my pension"
}
```

**Expected Response:**
```json
{
  "response": "Fraud analysis complete: No suspicious activity detected...",
  "user_id": 123,
  "data_source": "DATABASE_PENSION_DATA",
  "note": "This fraud detection analysis is based on your pension data stored in our database, not from uploaded documents."
}
```

**🔍 Key Indicator:** `"data_source": "DATABASE_PENSION_DATA"` confirms it used database data!

---

## 📄 **Test 3: PDF Search (Graceful Handling)**

### **3.1 PDF Query Without Uploaded PDFs**
```http
POST {{base_url}}/prompt
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "query": "What does my pension plan document say about retirement age?"
}
```

**Expected Response:**
```json
{
  "response": "I searched your uploaded documents but found no relevant information about retirement age. To get answers about your pension plan documents, you can: 1) Upload relevant PDF documents using the /upload_pdf endpoint, 2) Try rephrasing your question, 3) Ask about your current pension data instead...",
  "user_id": 123,
  "search_type": "PDF_DOCUMENT_SEARCH",
  "pdf_status": "NO_PDFS_FOUND",
  "note": "This response is from searching your uploaded PDF documents. No relevant documents were found for your query."
}
```

**🔍 Key Indicators:**
- `"search_type": "PDF_DOCUMENT_SEARCH"` - Confirms it searched PDFs
- `"pdf_status": "NO_PDFS_FOUND"` - Shows no PDFs were found
- `"note": "This response is from searching your uploaded PDF documents..."` - Clear explanation

**✅ This is expected behavior when no PDFs exist!**

### **3.2 PDF Query With Uploaded PDFs (Optional Test)**
```http
POST {{base_url}}/prompt
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "query": "What does my uploaded pension plan say about contribution limits?"
}
```

**Expected Response (if PDFs exist):**
```json
{
  "response": "Based on your uploaded pension plan document, the contribution limits are...",
  "user_id": 123,
  "search_type": "PDF_DOCUMENT_SEARCH",
  "pdf_status": "PDFS_FOUND_AND_SEARCHED",
  "note": "This response is based on content extracted from your uploaded PDF documents."
}
```

**🔍 Key Indicators:**
- `"search_type": "PDF_DOCUMENT_SEARCH"` - Confirms it searched PDFs
- `"pdf_status": "PDFS_FOUND_AND_SEARCHED"` - Shows PDFs were found and searched
- `"note": "This response is based on content extracted from your uploaded PDF documents."` - Clear explanation

---

## 📊 **Test 4: User Data Endpoints**

### **4.1 User Dashboard**
```http
GET {{base_url}}/resident/dashboard
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
  "user": {
    "id": 123,
    "full_name": "Test User",
    "email": "testuser@example.com",
    "role": "resident"
  },
  "pension_data": {
    "age": 35,
    "annual_income": 750000,
    "current_savings": 2500000,
    "retirement_age_goal": 60,
    "risk_tolerance": "Medium",
    "contribution_amount": 75000,
    "employer_contribution": 37500,
    "total_annual_contribution": 112500
  }
}
```

### **4.2 User Profile**
```http
GET {{base_url}}/users/me
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
  "id": 123,
  "full_name": "Test User",
  "email": "testuser@example.com",
  "role": "resident"
}
```

---

## 🔍 **Test 5: Health Check**

### **5.1 Server Health**
```http
GET {{base_url}}/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## 📱 **Optional: Test PDF Upload (If You Want)**

### **5.1 Upload PDF Document**
```http
POST {{base_url}}/upload_pdf
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data

file: [Select a PDF file]
```

**Expected Response:**
```json
{
  "status": "success",
  "filename": "pension_plan.pdf",
  "message": "Document ingested successfully"
}
```

### **5.2 Query About Uploaded PDF**
```http
POST {{base_url}}/prompt
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "query": "What does my uploaded pension plan say about contribution limits?"
}
```

**Expected Response:**
```json
{
  "response": "Based on your uploaded pension plan document, the contribution limits are...",
  "user_id": 123
}
```

---

## 🎯 **Testing Scenarios Summary**

| Test Type | PDF Required? | Purpose | Expected Outcome |
|-----------|---------------|---------|------------------|
| **Authentication** | ❌ No | User registration & login | JWT token received |
| **Basic Queries** | ❌ No | Pension data questions | Detailed responses |
| **Risk Analysis** | ❌ No | Risk assessment | Risk profile data |
| **Fraud Detection** | ❌ No | Security check | Fraud analysis results |
| **PDF Search** | ❌ No* | Document queries | Graceful "no PDFs" message |
| **User Dashboard** | ❌ No | Personal data view | Complete pension data |
| **PDF Upload** | ✅ Yes | Document ingestion | Success confirmation |
| **PDF Queries** | ✅ Yes* | Document-based answers | Content from PDFs |

*PDF queries work without PDFs but return helpful guidance messages.

---

## 🚨 **Common Issues & Solutions**

### **Issue: "User not authenticated"**
**Solution:** Make sure you're including the `Authorization: Bearer {{access_token}}` header

### **Issue: "No pension data found"**
**Solution:** The test user might not have pension data. Check if you need to create sample data first.

### **Issue: "Server connection refused"**
**Solution:** Make sure your FastAPI server is running on port 8000

### **Issue: "JWT token expired"**
**Solution:** Re-run the login request to get a fresh token

---

## 🎉 **Success Criteria**

✅ **All tests pass without errors**  
✅ **JWT authentication works**  
✅ **AI queries return meaningful responses**  
✅ **PDF search gracefully handles missing documents**  
✅ **User data endpoints return correct information**  
✅ **Server health check passes**  

---

## 🚀 **Next Steps After Testing**

1. **Frontend Integration**: Use the working endpoints in your React frontend
2. **PDF Upload**: Test with real pension documents
3. **Role-Based Testing**: Test advisor and regulator endpoints
4. **Performance Testing**: Test with multiple concurrent users

---

## 📞 **Need Help?**

If any tests fail:
1. Check the server logs for error messages
2. Verify your database connection
3. Ensure all environment variables are set
4. Check that the server is running on the correct port

**Happy Testing! 🧪✨**
