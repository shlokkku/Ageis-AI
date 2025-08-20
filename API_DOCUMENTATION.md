# 🚀 Pension AI API Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)
- [Testing Examples](#testing-examples)

---

## 🌟 Overview
The Pension AI API provides a comprehensive system for pension management, AI-powered queries, and role-based access control. The system supports multiple user roles: **Resident**, **Advisor**, **Supervisor**, and **Regulator**.

---

## 🔐 Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

**Token Format:** JWT (JSON Web Token)
**Expiration:** 24 hours from login

---

## 🌐 Base URL
```
http://localhost:8000
```

---

## 📡 Endpoints

### 1. 🔑 Authentication Endpoints

#### **POST /signup** - User Registration
**Description:** Create a new user account

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "role": "resident"
}
```

**Response (201 Created):**
```json
{
  "id": 123,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "role": "resident"
}
```

**Available Roles:** `resident`, `advisor`, `supervisor`, `regulator`

---

#### **POST /login** - User Authentication
**Description:** Authenticate user and receive JWT token

**Request Body (Form Data):**
```
username: john.doe@example.com
password: securepassword123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 123,
  "role": "resident",
  "full_name": "John Doe"
}
```

---

### 2. 🤖 AI Query Endpoints

#### **POST /prompt** - AI Pension Query
**Description:** Send AI-powered queries about pension data

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What will be my pension at retirement age?"
}
```

**Response (200 OK):**
```json
{
  "response": "Based on your current pension data, your projected pension at retirement age (65) will be approximately $45,000 annually...",
  "user_id": 123,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 3. 📄 Document Management

#### **POST /upload_pdf** - PDF Document Upload
**Description:** Upload PDF documents for pension analysis

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body (Form Data):**
```
file: <pdf_file>
```

**Response (200 OK):**
```json
{
  "message": "Document uploaded successfully",
  "filename": "pension_document.pdf",
  "user_id": 123
}
```

---

### 4. 📊 Data Retrieval Endpoints

#### **GET /output** - Role-Based Data
**Description:** Get data based on user role

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response by Role:**

**Resident:**
```json
{
  "role": "resident",
  "data": {
    "pension_summary": {
      "current_balance": 125000,
      "projected_retirement": 450000,
      "monthly_contribution": 500
    },
    "risk_profile": "Moderate",
    "retirement_age": 65
  }
}
```

**Advisor:**
```json
{
  "role": "advisor",
  "data": {
    "clients_count": 15,
    "total_portfolio_value": 2500000,
    "average_client_age": 42,
    "top_performing_funds": ["Fund A", "Fund B"]
  }
}
```

**Supervisor:**
```json
{
  "role": "supervisor",
  "data": {
    "categories": {
      "high_risk": {"count": 25, "total_value": 5000000},
      "moderate_risk": {"count": 45, "total_value": 8000000},
      "low_risk": {"count": 30, "total_value": 3000000}
    }
  }
}
```

**Regulator:**
```json
{
  "role": "regulator",
  "data": {
    "fraud_alerts": 3,
    "suspicious_transactions": 12,
    "total_users": 100,
    "compliance_score": 94.5
  }
}
```

---

#### **GET /dashboard/analytics** - Comprehensive Analytics
**Description:** Get detailed analytics data for dashboard

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "role": "advisor",
  "analytics": {
    "portfolio_distribution": {
      "equity": 60,
      "bonds": 25,
      "cash": 15
    },
    "performance_metrics": {
      "ytd_return": 8.5,
      "volatility": 12.3,
      "sharpe_ratio": 1.2
    },
    "client_demographics": {
      "age_groups": {"25-35": 20, "36-45": 35, "46-55": 30, "55+": 15},
      "income_ranges": {"<50k": 15, "50k-100k": 45, "100k+": 40}
    }
  }
}
```

---

#### **GET /users/{user_id}/dashboard** - Specific User Dashboard
**Description:** Get detailed dashboard for a specific user

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user_id": 123,
  "dashboard": {
    "personal_info": {
      "name": "John Doe",
      "age": 35,
      "risk_tolerance": "Moderate"
    },
    "pension_data": {
      "current_balance": 125000,
      "monthly_contribution": 500,
      "employer_match": 250,
      "projected_retirement": 450000
    },
    "investment_breakdown": {
      "fund_allocation": {"Fund A": 40, "Fund B": 35, "Fund C": 25},
      "asset_mix": {"Stocks": 60, "Bonds": 25, "Cash": 15}
    }
  }
}
```

---

### 5. 👥 Role-Specific Endpoints

#### **GET /resident/dashboard** - Resident Dashboard
**Description:** Get resident-specific dashboard data

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "personal_pension": {
    "current_balance": 125000,
    "monthly_contribution": 500,
    "employer_match": 250,
    "years_contributed": 8,
    "retirement_goal": 450000
  },
  "investment_performance": {
    "ytd_return": 8.5,
    "annualized_return": 7.2,
    "risk_level": "Moderate"
  }
}
```

---

#### **GET /advisor/dashboard** - Advisor Dashboard
**Description:** Get advisor-specific dashboard with client data

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "client_overview": {
    "total_clients": 15,
    "active_clients": 14,
    "total_portfolio": 2500000
  },
  "client_categories": {
    "high_risk": {"count": 5, "total_value": 800000},
    "moderate_risk": {"count": 7, "total_value": 1200000},
    "low_risk": {"count": 3, "total_value": 500000}
  },
  "performance_summary": {
    "average_client_return": 7.8,
    "top_performing_client": "Client A",
    "client_satisfaction_score": 4.6
  }
}
```

---

#### **GET /advisor/client/{client_id}/details** - Client Details
**Description:** Get detailed information about a specific client

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "client_id": 456,
  "personal_info": {
    "name": "Jane Smith",
    "age": 42,
    "employment_status": "Full-time",
    "annual_income": 85000
  },
  "pension_details": {
    "current_balance": 180000,
    "monthly_contribution": 600,
    "employer_match": 300,
    "risk_tolerance": "High",
    "retirement_goal": 600000
  },
  "investment_strategy": {
    "fund_allocation": {"Growth Fund": 70, "Income Fund": 20, "Cash": 10},
    "rebalancing_frequency": "Quarterly",
    "last_review": "2024-01-10"
  }
}
```

---

#### **GET /regulator/dashboard** - Regulator Dashboard
**Description:** Get regulator-specific fraud detection and compliance data

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "fraud_detection": {
    "active_alerts": 3,
    "suspicious_transactions": 12,
    "high_risk_users": 8,
    "anomaly_score_threshold": 0.7
  },
  "compliance_overview": {
    "total_users": 100,
    "compliant_users": 94,
    "compliance_score": 94.5,
    "last_audit": "2024-01-01"
  },
  "risk_categories": {
    "high_risk": {"count": 8, "total_value": 1200000},
    "medium_risk": {"count": 15, "total_value": 2500000},
    "low_risk": {"count": 77, "total_value": 15000000}
  }
}
```

---

#### **GET /regulator/user/{user_id}/details** - User Details for Regulator
**Description:** Get detailed user information for regulatory review

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user_id": 789,
  "risk_assessment": {
    "anomaly_score": 0.85,
    "suspicious_flags": 2,
    "transaction_pattern_score": 0.72,
    "fraud_probability": "High"
  },
  "transaction_history": {
    "recent_transactions": [
      {"amount": 5000, "date": "2024-01-15", "suspicious": true},
      {"amount": 2500, "date": "2024-01-10", "suspicious": false}
    ],
    "total_suspicious": 2,
    "total_amount": 7500
  },
  "compliance_status": {
    "kyc_verified": true,
    "aml_check": "Pending",
    "last_review": "2024-01-12",
    "risk_level": "High"
  }
}
```

---

### 6. 👤 User Management

#### **GET /users/me** - Current User Info
**Description:** Get current authenticated user information

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": 123,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "role": "resident",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 7. 🏥 Health Check

#### **GET /health** - System Health
**Description:** Check system health and version

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected",
  "ai_workflow": "operational"
}
```

---

## ❌ Error Handling

### **Common Error Responses:**

#### **400 Bad Request**
```json
{
  "detail": "Invalid request data"
}
```

#### **401 Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```

#### **403 Forbidden**
```json
{
  "detail": "Insufficient permissions"
}
```

#### **404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

#### **422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

#### **500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Testing Examples

### **Using cURL:**

#### **1. User Registration:**
```bash
curl -X POST "http://localhost:8000/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "resident"
  }'
```

#### **2. User Login:**
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

#### **3. AI Query (with JWT):**
```bash
curl -X POST "http://localhost:8000/prompt" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is my pension projection?"}'
```

#### **4. Get Dashboard Data:**
```bash
curl -X GET "http://localhost:8000/dashboard/analytics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **Using Python Requests:**

```python
import requests

# Base URL
base_url = "http://localhost:8000"

# 1. Register user
signup_data = {
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "resident"
}
response = requests.post(f"{base_url}/signup", json=signup_data)
print("Signup:", response.json())

# 2. Login
login_data = {
    "username": "test@example.com",
    "password": "testpass123"
}
response = requests.post(f"{base_url}/login", data=login_data)
token = response.json()["access_token"]

# 3. Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Get user dashboard
response = requests.get(f"{base_url}/resident/dashboard", headers=headers)
print("Dashboard:", response.json())

# Send AI query
query_data = {"query": "What will be my pension at retirement?"}
response = requests.post(f"{base_url}/prompt", json=query_data, headers=headers)
print("AI Response:", response.json())
```

---

## 🔧 Environment Variables

Create a `.env` file in the `server` directory:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/pension_db

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Configuration
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

---

## 🚀 Getting Started

### **1. Install Dependencies:**
```bash
cd server
pip install -r requirements.txt
```

### **2. Set Environment Variables:**
```bash
# Copy and configure .env file
cp env_template.txt .env
# Edit .env with your actual values
```

### **3. Start Server:**
```bash
python start_server.py
# Or directly:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### **4. Test API:**
```bash
# Health check
curl http://localhost:8000/health

# Run test script
python test_api.py
```

---

## 📊 Database Schema

### **Users Table:**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('resident', 'advisor', 'supervisor', 'regulator') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Pension Data Table:**
```sql
CREATE TABLE pension_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    age INT,
    gender VARCHAR(10),
    country VARCHAR(100),
    employment_status VARCHAR(50),
    annual_income DECIMAL(15,2),
    current_savings DECIMAL(15,2),
    retirement_age_goal INT,
    risk_tolerance VARCHAR(20),
    contribution_amount DECIMAL(10,2),
    contribution_frequency VARCHAR(20),
    employer_contribution DECIMAL(10,2),
    total_annual_contribution DECIMAL(15,2),
    years_contributed INT,
    investment_type VARCHAR(50),
    fund_name VARCHAR(100),
    annual_return_rate DECIMAL(5,2),
    volatility DECIMAL(5,2),
    fees_percentage DECIMAL(5,2),
    projected_pension_amount DECIMAL(15,2),
    expected_annual_payout DECIMAL(15,2),
    inflation_adjusted_payout DECIMAL(15,2),
    years_of_payout INT,
    survivor_benefits BOOLEAN,
    transaction_id VARCHAR(100),
    transaction_amount DECIMAL(15,2),
    transaction_date TIMESTAMP,
    suspicious_flag BOOLEAN,
    anomaly_score DECIMAL(5,2),
    marital_status VARCHAR(20),
    number_of_dependents INT,
    education_level VARCHAR(50),
    health_status VARCHAR(50),
    life_expectancy_estimate INT,
    home_ownership_status VARCHAR(20),
    debt_level DECIMAL(15,2),
    monthly_expenses DECIMAL(15,2),
    savings_rate DECIMAL(5,2),
    investment_experience_level VARCHAR(20),
    financial_goals TEXT,
    insurance_coverage DECIMAL(15,2),
    portfolio_diversity_score DECIMAL(5,2),
    tax_benefits_eligibility BOOLEAN,
    government_pension_eligibility BOOLEAN,
    private_pension_eligibility BOOLEAN,
    pension_type VARCHAR(50),
    withdrawal_strategy VARCHAR(50),
    transaction_channel VARCHAR(50),
    ip_address VARCHAR(45),
    device_id VARCHAR(100),
    geo_location VARCHAR(100),
    time_of_transaction TIMESTAMP,
    transaction_pattern_score DECIMAL(5,2),
    previous_fraud_flag BOOLEAN,
    account_age INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### **Advisor Clients Table:**
```sql
CREATE TABLE advisor_clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    advisor_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (advisor_id) REFERENCES users(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🎯 Role-Based Access Matrix

| Endpoint | Resident | Advisor | Supervisor | Regulator |
|-----------|----------|---------|------------|-----------|
| `/signup` | ✅ | ✅ | ✅ | ✅ |
| `/login` | ✅ | ✅ | ✅ | ✅ |
| `/prompt` | ✅ | ✅ | ✅ | ✅ |
| `/upload_pdf` | ✅ | ✅ | ✅ | ✅ |
| `/output` | ✅ | ✅ | ✅ | ✅ |
| `/dashboard/analytics` | ✅ | ✅ | ✅ | ✅ |
| `/users/me` | ✅ | ✅ | ✅ | ✅ |
| `/resident/dashboard` | ✅ | ❌ | ❌ | ❌ |
| `/advisor/dashboard` | ❌ | ✅ | ❌ | ❌ |
| `/advisor/client/{id}` | ❌ | ✅ | ❌ | ❌ |
| `/regulator/dashboard` | ❌ | ❌ | ❌ | ✅ |
| `/regulator/user/{id}` | ❌ | ❌ | ❌ | ✅ |
| `/users/{id}/dashboard` | ❌ | ✅ | ✅ | ✅ |

---

## 🔍 Troubleshooting

### **Common Issues:**

1. **"Incorrect email or password"**
   - Check if user exists in database
   - Verify password was hashed correctly during signup
   - Ensure login uses `username` field (not `email`)

2. **"Not authenticated"**
   - Include JWT token in Authorization header
   - Check if token is expired
   - Verify token format: `Bearer <token>`

3. **"Insufficient permissions"**
   - Check user role has access to endpoint
   - Verify JWT token belongs to correct user

4. **Database Connection Issues**
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure database exists

---

## 📞 Support

For technical support or questions:
- Check the logs in your terminal
- Verify all environment variables are set
- Ensure database schema matches the provided structure
- Test with the provided examples first

---

**🎉 Happy Coding with Pension AI API! 🚀**
