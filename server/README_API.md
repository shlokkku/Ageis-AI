# Pension AI API Documentation

## Overview

The Pension AI API is a comprehensive FastAPI-based system that provides pension analysis, fraud detection, and risk assessment capabilities. The system uses AI agents to process user queries and return intelligent responses with visualizations.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/signup` and `/login`) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. User Management

#### POST /signup
User registration endpoint.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "role": "resident"
}
```

**Valid Roles:**
- `resident` - Pension plan participants
- `advisor` - Financial advisors
- `regulator` - Regulatory authorities
- `supervisor` - System supervisors

**Response:**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "role": "resident"
}
```

#### POST /login
User authentication endpoint.

**Request Body (Form Data):**
```
username: john@example.com
password: securepassword123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "role": "resident",
  "full_name": "John Doe"
}
```

### 2. AI Query Processing

#### POST /prompt
Main AI query endpoint that processes pension-related questions.

**Request Body:**
```json
{
  "query": "What's my pension balance and risk profile?"
}
```

**Response:**
```json
{
  "summary": "Based on your pension data, you currently have $150,000 in savings...",
  "chart_data": {
    "risk_score": 0.7,
    "projected_amount": 450000
  },
  "plotly_figures": {
    "risk_chart": {...},
    "projection_chart": {...}
  },
  "chart_images": {},
  "metadata": {
    "user_id": 1,
    "query": "What's my pension balance and risk profile?",
    "workflow_completed": true
  }
}
```

### 3. Document Management

#### POST /upload_pdf
Upload PDF documents for AI processing and knowledge base ingestion.

**Request:**
- Content-Type: `multipart/form-data`
- File: PDF document

**Response:**
```json
{
  "status": "success",
  "filename": "pension_document.pdf",
  "message": "Document ingested successfully"
}
```

### 4. Data Retrieval

#### GET /output
Role-based data retrieval endpoint that returns grouped data based on user role.

**Response Examples:**

**Resident:**
```json
{
  "data": [
    {
      "category": "Personal",
      "count": 1,
      "users": [
        {
          "user_id": 1,
          "full_name": "John Doe",
          "age": 35,
          "risk_tolerance": "Medium",
          "current_savings": 150000,
          "projected_pension_amount": 450000,
          "fraud_risk": "False",
          "anomaly_score": 0.2
        }
      ]
    }
  ],
  "total_users": 1
}
```

**Advisor:**
```json
{
  "data": [
    {
      "category": "Low",
      "count": 5,
      "users": [...]
    },
    {
      "category": "Medium",
      "count": 8,
      "users": [...]
    },
    {
      "category": "High",
      "count": 3,
      "users": [...]
    }
  ],
  "total_users": 16
}
```

**Supervisor:**
```json
{
  "data": [
    {
      "category": "Age Groups: 30-39",
      "count": 25,
      "users": [...]
    },
    {
      "category": "Risk Tolerance: Medium",
      "count": 45,
      "users": [...]
    },
    {
      "category": "Income Levels: Medium ($50k-$100k)",
      "count": 38,
      "users": [...]
    }
  ],
  "total_users": 150
}
```

**Regulator:**
```json
{
  "data": [
    {
      "category": "High Risk",
      "count": 12,
      "users": [...]
    },
    {
      "category": "Medium Risk",
      "count": 28,
      "users": [...]
    },
    {
      "category": "Low Risk",
      "count": 110,
      "users": [...]
    }
  ],
  "total_users": 150
}
```

### 5. Dashboard Analytics

#### GET /dashboard/analytics
Comprehensive analytics endpoint for creating dashboard visualizations.

**Query Parameters:**
- `category` (optional): Specific category for grouping data

**Available Categories by Role:**
- **Advisor**: `risk_tolerance`, `age_group`, `income_level`
- **Supervisor**: `age_groups`, `risk_tolerance`, `fraud_risk`, `overall`
- **Regulator**: Fraud-focused analytics (no category parameter needed)

**Response Examples:**

**Resident Analytics:**
```json
{
  "role": "resident",
  "user_id": 1,
  "analytics": {
    "pension_overview": {
      "current_savings": 150000,
      "projected_amount": 450000,
      "annual_income": 75000,
      "contribution_rate": 5000,
      "years_to_retirement": 30
    },
    "risk_profile": {
      "risk_tolerance": "Medium",
      "volatility": 0.15,
      "portfolio_diversity": 0.7,
      "debt_ratio": 0.3
    },
    "fraud_indicators": {
      "anomaly_score": 0.2,
      "suspicious_flag": "False",
      "transaction_amount": 5000,
      "geo_location": "New York, NY"
    }
  }
}
```

**Supervisor Analytics (Overall):**
```json
{
  "role": "supervisor",
  "analytics": {
    "Overall": {
      "total_users": 150,
      "avg_age": 42.5,
      "avg_savings": 125000,
      "avg_income": 68000,
      "risk_distribution": {
        "low": 45,
        "medium": 78,
        "high": 27
      },
      "fraud_risk_distribution": {
        "high": 12,
        "medium": 28,
        "low": 110
      }
    }
  },
  "total_users": 150,
  "available_categories": ["age_groups", "risk_tolerance", "fraud_risk", "overall"]
}
```

### 6. User Dashboard

#### GET /users/{user_id}/dashboard
Get detailed dashboard data for a specific user.

**Path Parameters:**
- `user_id`: ID of the user to view

**Response:**
```json
{
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "resident"
  },
  "pension_data": {
    "age": 35,
    "risk_tolerance": "Medium",
    "current_savings": 150000,
    "annual_income": 75000,
    "projected_pension_amount": 450000,
    "fraud_risk": "False",
    "anomaly_score": 0.2,
    "portfolio_diversity_score": 0.7,
    "volatility": 0.15
  }
}
```

### 7. Utility Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Pension AI API",
  "version": "1.0.0"
}
```

#### GET /users/me
Get current user information.

**Response:**
```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "role": "resident"
}
```

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "detail": "Error message description"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Role-Based Access Control

### Resident
- View own pension data
- Upload documents
- Query AI system about personal pension
- Access personal dashboard

### Advisor
- View client data grouped by categories
- Access client analytics
- Query AI system for client insights
- Manage client relationships

### Supervisor
- View all user data grouped by multiple categories
- Access comprehensive analytics
- Query AI system for system-wide insights
- Monitor overall pension system health

### Regulator
- View fraud-focused data
- Access fraud risk analytics
- Query AI system for compliance insights
- Monitor suspicious activities

## AI Workflow Integration

The `/prompt` endpoint integrates with a sophisticated AI workflow that includes:

1. **Supervisor Agent** - Routes queries to appropriate specialists
2. **Risk Agent** - Analyzes risk profiles and portfolio composition
3. **Fraud Agent** - Detects suspicious transactions and patterns
4. **Pension Agent** - Provides pension projections and calculations
5. **Visualizer Agent** - Creates charts and graphs when requested
6. **Summarizer Agent** - Consolidates responses into coherent summaries

## Data Flow

1. User logs in → receives JWT token
2. User sends query with JWT token
3. FastAPI validates JWT → extracts user_id
4. AI workflow executes with user context
5. Tools use user_id for database queries
6. Response returned with user-specific data

## Security Features

- JWT-based authentication
- Role-based access control
- Request-scoped user context
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM

## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
SECRET_KEY=your_secret_key
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pension_db
GEMINI_API_KEY=your_gemini_api_key
```

3. Run the server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

Test the API endpoints using tools like:
- Postman
- curl
- FastAPI's automatic interactive docs at `/docs`

## Frontend Integration

The API is designed to work with modern frontend frameworks:
- React/Vue.js for dynamic dashboards
- Plotly.js for interactive visualizations
- JWT token management for authentication
- Real-time data updates via polling or WebSockets
