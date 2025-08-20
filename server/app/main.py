# main.py
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import os
import shutil
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from .database import Base, engine, get_db
from . import models, security, schemas
from .workflow import graph
from file_ingestion import ingest_pdf_to_chroma
from .tools.tools import set_request_user_id, clear_request_user_id

app = FastAPI(title="Pension AI API", version="1.0.0")

# ---------------------------
# CORS Configuration
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Create database tables
# ---------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------
# Request/Response Models
# ---------------------------
class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    full_name: str

class PromptRequest(BaseModel):
    query: str

class PromptResponse(BaseModel):
    summary: str
    chart_data: Optional[Dict[str, Any]] = None
    plotly_figures: Optional[Dict[str, Any]] = None
    chart_images: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    # 🔍 ADD DATA SOURCE INDICATORS (NEW ADDITION)
    data_source: Optional[str] = None
    search_type: Optional[str] = None
    pdf_status: Optional[str] = None

class DashboardData(BaseModel):
    user_id: int
    full_name: str
    age: Optional[int]
    risk_tolerance: Optional[str]
    current_savings: Optional[float]
    projected_pension_amount: Optional[float]
    fraud_risk: Optional[str]
    anomaly_score: Optional[float]

class CategoryGroupedData(BaseModel):
    category: str
    count: int
    users: List[DashboardData]

class OutputResponse(BaseModel):
    data: List[CategoryGroupedData]
    total_users: int

# ---------------------------
# Authentication dependency
# ---------------------------
oauth2_scheme = HTTPBearer()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Get current authenticated user from JWT token"""
    try:
        payload = security.decode_jwt(token.credentials)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---------------------------
# Core Endpoints
# ---------------------------

@app.post("/signup", response_model=schemas.UserResponse)
async def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """User registration endpoint"""
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    valid_roles = ["resident", "advisor", "regulator", "supervisor"]
    if user_data.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Create new user
    hashed_password = security.hash_password(user_data.password)
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return user data without password
    return schemas.UserResponse(
        id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        role=new_user.role
    )

@app.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """User authentication endpoint"""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"user_id": user.id, "role": user.role}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role,
        full_name=user.full_name
    )

@app.post("/prompt", response_model=PromptResponse)
async def process_prompt(
    request: PromptRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Main AI query endpoint that processes pension queries"""
    try:
        # Set user context for this request
        set_request_user_id(current_user.id)
        
        # Execute the workflow with the user's query AND user_id
        result = graph.invoke({
            'messages': [('user', request.query)],
            'user_id': current_user.id  # Pass user_id directly to workflow
        })
        
        # Extract the final response
        final_response = result.get('final_response', {})
        
        # Return structured response
        return PromptResponse(
            summary=final_response.get('summary', 'No summary available'),
            chart_data=final_response.get('charts', {}),
            plotly_figures=final_response.get('plotly_figs', {}),
            chart_images=final_response.get('chart_images', {}),
            metadata={
                'user_id': current_user.id,
                'query': request.query,
                'workflow_completed': True
            },
            # 🔍 INCLUDE THE DATA SOURCE INDICATORS (NEW ADDITION)
            data_source=final_response.get('data_source'),
            search_type=final_response.get('search_type'),
            pdf_status=final_response.get('pdf_status')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")
    
    finally:
        # Clean up request context
        clear_request_user_id()

@app.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    """PDF document ingestion endpoint"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = ingest_pdf_to_chroma(file_path, user_id=current_user.id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return {"status": "success", "filename": file.filename, "message": "Document ingested successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ---------------------------
# Role-Based Endpoints
# ---------------------------

@app.get("/resident/dashboard")
async def get_resident_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Resident dashboard - personal pension data"""
    if current_user.role != "resident":
        raise HTTPException(status_code=403, detail="Only residents can access this endpoint")
    
    # Get resident's pension data
    pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == current_user.id).first()
    if not pension_data:
        raise HTTPException(status_code=404, detail="No pension data found")
    
    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role
        },
        "pension_data": {
            "age": pension_data.age,
            "gender": pension_data.gender,
            "country": pension_data.country,
            "employment_status": pension_data.employment_status,
            "annual_income": pension_data.annual_income,
            "current_savings": pension_data.current_savings,
            "retirement_age_goal": pension_data.retirement_age_goal,
            "risk_tolerance": pension_data.risk_tolerance,
            "contribution_amount": pension_data.contribution_amount,
            "employer_contribution": pension_data.employer_contribution,
            "total_annual_contribution": pension_data.total_annual_contribution,
            "years_contributed": pension_data.years_contributed,
            "projected_pension_amount": pension_data.projected_pension_amount,
            "expected_annual_payout": pension_data.expected_annual_payout,
            "portfolio_diversity_score": pension_data.portfolio_diversity_score,
            "volatility": pension_data.volatility,
            "fraud_risk": pension_data.suspicious_flag,
            "anomaly_score": pension_data.anomaly_score
        }
    }

@app.get("/advisor/dashboard")
async def get_advisor_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Advisor dashboard - client data grouped by categories"""
    if current_user.role != "advisor":
        raise HTTPException(status_code=403, detail="Only advisors can access this endpoint")
    
    # Get all clients for this advisor using raw SQL
    client_query = text("""
        SELECT 
            u.id as user_id,
            u.full_name,
            p.age,
            p.gender,
            p.country,
            p.employment_status,
            p.annual_income,
            p.current_savings,
            p.retirement_age_goal,
            p.risk_tolerance,
            p.contribution_amount,
            p.employer_contribution,
            p.total_annual_contribution,
            p.years_contributed,
            p.projected_pension_amount,
            p.expected_annual_payout,
            p.portfolio_diversity_score,
            p.volatility,
            p.suspicious_flag,
            p.anomaly_score,
            p.marital_status,
            p.number_of_dependents,
            p.education_level,
            p.health_status,
            p.debt_level,
            p.monthly_expenses,
            p.savings_rate,
            p.investment_experience_level,
            p.financial_goals,
            p.insurance_coverage,
            p.pension_type
        FROM users u
        INNER JOIN advisor_clients ac ON u.id = ac.resident_id
        INNER JOIN pension_data p ON u.id = p.user_id
        WHERE ac.advisor_id = :advisor_id
    """)
    
    result = db.execute(client_query, {"advisor_id": current_user.id})
    clients_data = result.fetchall()
    
    if not clients_data:
        return {
            "advisor_id": current_user.id,
            "total_clients": 0,
            "grouped_data": {},
            "summary": {
                "total_clients": 0,
                "avg_age": 0,
                "avg_income": 0,
                "avg_savings": 0,
                "risk_distribution": {},
                "fraud_risk_summary": {}
            }
        }
    
    # Group clients by risk tolerance
    risk_groups = {}
    age_groups = {}
    income_groups = {}
    
    total_clients = len(clients_data)
    total_age = 0
    total_income = 0
    total_savings = 0
    risk_distribution = {}
    fraud_risk_summary = {"high": 0, "medium": 0, "low": 0}
    
    for client in clients_data:
        # Risk tolerance grouping
        risk = client.risk_tolerance or "Unknown"
        if risk not in risk_groups:
            risk_groups[risk] = []
        risk_groups[risk].append(client)
        
        # Age grouping
        if client.age:
            age_group = f"{(client.age // 10) * 10}-{(client.age // 10) * 10 + 9}"
            if age_group not in age_groups:
                age_groups[age_group] = []
            age_groups[age_group].append(client)
        
        # Income grouping
        if client.annual_income:
            if client.annual_income < 50000:
                income_group = "Low (<$50k)"
            elif client.annual_income < 100000:
                income_group = "Medium ($50k-$100k)"
            else:
                income_group = "High (>$100k)"
            
            if income_group not in income_groups:
                income_groups[income_group] = []
            income_groups[income_group].append(client)
        
        # Calculate totals for summary
        if client.age:
            total_age += client.age
        if client.annual_income:
            total_income += client.annual_income
        if client.current_savings:
            total_savings += client.current_savings
        
        # Risk distribution
        if risk not in risk_distribution:
            risk_distribution[risk] = 0
        risk_distribution[risk] += 1
        
        # Fraud risk summary
        if client.anomaly_score:
            if client.anomaly_score > 0.8:
                fraud_risk_summary["high"] += 1
            elif client.anomaly_score > 0.5:
                fraud_risk_summary["medium"] += 1
            else:
                fraud_risk_summary["low"] += 1
    
    # Calculate averages
    avg_age = total_age / total_clients if total_clients > 0 else 0
    avg_income = total_income / total_clients if total_clients > 0 else 0
    avg_savings = total_savings / total_clients if total_clients > 0 else 0
    
    return {
        "advisor_id": current_user.id,
        "total_clients": total_clients,
        "grouped_data": {
            "by_risk_tolerance": {
                risk: {
                    "count": len(clients),
                    "clients": [
                        {
                            "user_id": c.user_id,
                            "full_name": c.full_name,
                            "age": c.age,
                            "annual_income": c.annual_income,
                            "current_savings": c.current_savings,
                            "risk_tolerance": c.risk_tolerance,
                            "anomaly_score": c.anomaly_score
                        } for c in clients
                    ]
                } for risk, clients in risk_groups.items()
            },
            "by_age_group": {
                age_group: {
                    "count": len(clients),
                    "clients": [
                        {
                            "user_id": c.user_id,
                            "full_name": c.full_name,
                            "age": c.age,
                            "annual_income": c.annual_income,
                            "current_savings": c.current_savings,
                            "risk_tolerance": c.risk_tolerance
                        } for c in clients
                    ]
                } for age_group, clients in age_groups.items()
            },
            "by_income_level": {
                income_group: {
                    "count": len(clients),
                    "clients": [
                        {
                            "user_id": c.user_id,
                            "full_name": c.full_name,
                            "age": c.age,
                            "annual_income": c.annual_income,
                            "current_savings": c.current_savings,
                            "risk_tolerance": c.risk_tolerance
                        } for c in clients
                    ]
                } for income_group, clients in income_groups.items()
            }
        },
        "summary": {
            "total_clients": total_clients,
            "avg_age": round(avg_age, 1),
            "avg_income": round(avg_income, 2),
            "avg_savings": round(avg_savings, 2),
            "risk_distribution": risk_distribution,
            "fraud_risk_summary": fraud_risk_summary
        }
    }

@app.get("/regulator/dashboard")
async def get_regulator_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Regulator dashboard - fraud-focused data and risk analysis"""
    if current_user.role != "regulator":
        raise HTTPException(status_code=403, detail="Only regulators can access this endpoint")
    
    # Get all pension data for fraud analysis using raw SQL
    fraud_query = text("""
        SELECT 
            u.id as user_id,
            u.full_name,
            u.email,
            p.age,
            p.gender,
            p.country,
            p.annual_income,
            p.current_savings,
            p.risk_tolerance,
            p.suspicious_flag,
            p.anomaly_score,
            p.transaction_amount,
            p.transaction_date,
            p.geo_location,
            p.ip_address,
            p.device_id,
            p.time_of_transaction,
            p.transaction_pattern_score,
            p.previous_fraud_flag,
            p.account_age,
            p.portfolio_diversity_score,
            p.volatility,
            p.debt_level,
            p.monthly_expenses,
            p.savings_rate
        FROM users u
        INNER JOIN pension_data p ON u.id = p.user_id
        ORDER BY p.anomaly_score DESC NULLS LAST
    """)
    
    result = db.execute(fraud_query)
    all_data = result.fetchall()
    
    if not all_data:
        return {
            "total_users": 0,
            "fraud_analysis": {},
            "risk_distribution": {},
            "geographic_analysis": {}
        }
    
    # Fraud risk analysis
    fraud_groups = {
        "High Risk": [],
        "Medium Risk": [],
        "Low Risk": [],
        "Unknown": []
    }
    
    # Geographic analysis
    geographic_data = {}
    
    # Risk distribution
    risk_distribution = {}
    
    total_users = len(all_data)
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    total_suspicious = 0
    
    for data in all_data:
        # Categorize by fraud risk
        if data.anomaly_score and data.anomaly_score > 0.8:
            fraud_groups["High Risk"].append(data)
            high_risk_count += 1
        elif data.anomaly_score and data.anomaly_score > 0.5:
            fraud_groups["Medium Risk"].append(data)
            medium_risk_count += 1
        elif data.anomaly_score and data.anomaly_score <= 0.5:
            fraud_groups["Low Risk"].append(data)
            low_risk_count += 1
        else:
            fraud_groups["Unknown"].append(data)
        
        # Geographic analysis
        geo = data.geo_location or "Unknown"
        if geo not in geographic_data:
            geographic_data[geo] = {
                "count": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "total_anomaly_score": 0
            }
        
        geographic_data[geo]["count"] += 1
        if data.anomaly_score:
            geographic_data[geo]["total_anomaly_score"] += data.anomaly_score
            
            if data.anomaly_score > 0.8:
                geographic_data[geo]["high_risk"] += 1
            elif data.anomaly_score > 0.5:
                geographic_data[geo]["medium_risk"] += 1
            else:
                geographic_data[geo]["low_risk"] += 1
        
        # Risk tolerance distribution
        risk = data.risk_tolerance or "Unknown"
        if risk not in risk_distribution:
            risk_distribution[risk] = 0
        risk_distribution[risk] += 1
        
        # Count suspicious transactions
        if data.suspicious_flag == "True":
            total_suspicious += 1
    
    # Calculate geographic averages
    for geo in geographic_data:
        if geographic_data[geo]["count"] > 0:
            geographic_data[geo]["avg_anomaly_score"] = round(
                geographic_data[geo]["total_anomaly_score"] / geographic_data[geo]["count"], 3
            )
    
    return {
        "total_users": total_users,
        "fraud_analysis": {
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
            "total_suspicious": total_suspicious,
            "risk_groups": {
                risk_level: {
                    "count": len(data_list),
                    "users": [
                        {
                            "user_id": d.user_id,
                            "full_name": d.full_name,
                            "age": d.age,
                            "country": d.country,
                            "annual_income": d.annual_income,
                            "anomaly_score": d.anomaly_score,
                            "suspicious_flag": d.suspicious_flag,
                            "transaction_amount": d.transaction_amount,
                            "geo_location": d.geo_location,
                            "ip_address": d.ip_address,
                            "transaction_pattern_score": d.transaction_pattern_score,
                            "previous_fraud_flag": d.previous_fraud_flag
                        } for d in data_list
                    ]
                } for risk_level, data_list in fraud_groups.items() if data_list
            }
        },
        "risk_distribution": risk_distribution,
        "geographic_analysis": geographic_data
    }

@app.get("/regulator/user/{user_id}/details")
async def get_regulator_user_details(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user information for regulators"""
    if current_user.role != "regulator":
        raise HTTPException(status_code=403, detail="Only regulators can access this endpoint")
    
    # Get detailed user and pension data using raw SQL
    user_query = text("""
        SELECT 
            u.id as user_id,
            u.full_name,
            u.email,
            u.role,
            p.*
        FROM users u
        INNER JOIN pension_data p ON u.id = p.user_id
        WHERE u.id = :user_id
    """)
    
    result = db.execute(user_query, {"user_id": user_id})
    user_data = result.fetchone()
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": {
            "id": user_data.user_id,
            "full_name": user_data.full_name,
            "email": user_data.email,
            "role": user_data.role
        },
        "pension_data": {
            "demographics": {
                "age": user_data.age,
                "gender": user_data.gender,
                "country": user_data.country,
                "employment_status": user_data.employment_status,
                "marital_status": user_data.marital_status,
                "number_of_dependents": user_data.number_of_dependents,
                "education_level": user_data.education_level,
                "health_status": user_data.health_status,
                "life_expectancy_estimate": user_data.life_expectancy_estimate
            },
            "financial": {
                "annual_income": user_data.annual_income,
                "current_savings": user_data.current_savings,
                "debt_level": user_data.debt_level,
                "monthly_expenses": user_data.monthly_expenses,
                "savings_rate": user_data.savings_rate,
                "contribution_amount": user_data.contribution_amount,
                "employer_contribution": user_data.employer_contribution,
                "total_annual_contribution": user_data.total_annual_contribution
            },
            "pension": {
                "retirement_age_goal": user_data.retirement_age_goal,
                "years_contributed": user_data.years_contributed,
                "projected_pension_amount": user_data.projected_pension_amount,
                "expected_annual_payout": user_data.expected_annual_payout,
                "pension_type": user_data.pension_type,
                "withdrawal_strategy": user_data.withdrawal_strategy
            },
            "investment": {
                "risk_tolerance": user_data.risk_tolerance,
                "investment_type": user_data.investment_type,
                "fund_name": user_data.fund_name,
                "annual_return_rate": user_data.annual_return_rate,
                "volatility": user_data.volatility,
                "portfolio_diversity_score": user_data.portfolio_diversity_score
            },
            "fraud_indicators": {
                "suspicious_flag": user_data.suspicious_flag,
                "anomaly_score": user_data.anomaly_score,
                "transaction_amount": user_data.transaction_amount,
                "transaction_date": user_data.transaction_date,
                "transaction_channel": user_data.transaction_channel,
                "ip_address": user_data.ip_address,
                "device_id": user_data.device_id,
                "geo_location": user_data.geo_location,
                "time_of_transaction": user_data.time_of_transaction,
                "transaction_pattern_score": user_data.transaction_pattern_score,
                "previous_fraud_flag": user_data.previous_fraud_flag,
                "account_age": user_data.account_age
            }
        }
    }

@app.get("/advisor/client/{client_id}/details")
async def get_advisor_client_details(
    client_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed client information for advisors"""
    if current_user.role != "advisor":
        raise HTTPException(status_code=403, detail="Only advisors can access this endpoint")
    
    # Verify client relationship
    client_relationship = db.query(models.AdvisorClient).filter(
        models.AdvisorClient.advisor_id == current_user.id,
        models.AdvisorClient.resident_id == client_id
    ).first()
    
    if not client_relationship:
        raise HTTPException(status_code=403, detail="Client not in your client list")
    
    # Get detailed client data using raw SQL
    client_query = text("""
        SELECT 
            u.id as user_id,
            u.full_name,
            u.email,
            p.*
        FROM users u
        INNER JOIN pension_data p ON u.id = p.user_id
        WHERE u.id = :client_id
    """)
    
    result = db.execute(client_query, {"client_id": client_id})
    client_data = result.fetchone()
    
    if not client_data:
        raise HTTPException(status_code=404, detail="Client data not found")
    
    return {
        "client": {
            "id": client_data.user_id,
            "full_name": client_data.full_name,
            "email": client_data.email
        },
        "pension_data": {
            "demographics": {
                "age": client_data.age,
                "gender": client_data.gender,
                "country": client_data.country,
                "employment_status": client_data.employment_status,
                "marital_status": client_data.marital_status,
                "number_of_dependents": client_data.number_of_dependents,
                "education_level": client_data.education_level,
                "health_status": client_data.health_status
            },
            "financial": {
                "annual_income": client_data.annual_income,
                "current_savings": client_data.current_savings,
                "debt_level": client_data.debt_level,
                "monthly_expenses": client_data.monthly_expenses,
                "savings_rate": client_data.savings_rate,
                "contribution_amount": client_data.contribution_amount,
                "employer_contribution": client_data.employer_contribution,
                "total_annual_contribution": client_data.total_annual_contribution
            },
            "pension": {
                "retirement_age_goal": client_data.retirement_age_goal,
                "years_contributed": client_data.years_contributed,
                "projected_pension_amount": client_data.projected_pension_amount,
                "expected_annual_payout": client_data.expected_annual_payout,
                "pension_type": client_data.pension_type
            },
            "investment": {
                "risk_tolerance": client_data.risk_tolerance,
                "investment_type": client_data.investment_type,
                "fund_name": client_data.fund_name,
                "annual_return_rate": client_data.annual_return_rate,
                "volatility": client_data.volatility,
                "portfolio_diversity_score": client_data.portfolio_diversity_score
            },
            "risk_indicators": {
                "suspicious_flag": client_data.suspicious_flag,
                "anomaly_score": client_data.anomaly_score,
                "transaction_amount": client_data.transaction_amount,
                "transaction_date": client_data.transaction_date
            }
        }
    }

# ---------------------------
# Legacy endpoints for backward compatibility
# ---------------------------

@app.get("/output", response_model=OutputResponse)
async def get_output_data(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Legacy endpoint - redirects to role-specific endpoints"""
    if current_user.role == "resident":
        # Redirect to resident dashboard
        pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == current_user.id).first()
        if not pension_data:
            raise HTTPException(status_code=404, detail="No pension data found")
        
        user_data = DashboardData(
            user_id=current_user.id,
            full_name=current_user.full_name,
            age=pension_data.age,
            risk_tolerance=pension_data.risk_tolerance,
            current_savings=pension_data.current_savings,
            projected_pension_amount=pension_data.projected_pension_amount,
            fraud_risk=pension_data.suspicious_flag,
            anomaly_score=pension_data.anomaly_score
        )
        
        return OutputResponse(
            data=[CategoryGroupedData(category="Personal", count=1, users=[user_data])],
            total_users=1
        )
    
    elif current_user.role == "advisor":
        # Get advisor dashboard data
        dashboard_data = await get_advisor_dashboard(current_user, db)
        
        # Convert to legacy format
        grouped_data = []
        for risk, data in dashboard_data["grouped_data"]["by_risk_tolerance"].items():
            users = [
                DashboardData(
                    user_id=c["user_id"],
                    full_name=c["full_name"],
                    age=c["age"],
                    risk_tolerance=c["risk_tolerance"],
                    current_savings=c["current_savings"],
                    projected_pension_amount=0,  # Not available in advisor view
                    fraud_risk="Unknown",
                    anomaly_score=c["anomaly_score"]
                ) for c in data["clients"]
            ]
            grouped_data.append(CategoryGroupedData(category=risk, count=data["count"], users=users))
        
        return OutputResponse(data=grouped_data, total_users=dashboard_data["total_clients"])
    
    elif current_user.role == "regulator":
        # Get regulator dashboard data
        dashboard_data = await get_regulator_dashboard(current_user, db)
        
        # Convert to legacy format
        grouped_data = []
        for risk_level, data in dashboard_data["fraud_analysis"]["risk_groups"].items():
            users = [
                DashboardData(
                    user_id=u["user_id"],
                    full_name=u["full_name"],
                    age=u["age"],
                    risk_tolerance="Unknown",
                    current_savings=0,
                    projected_pension_amount=0,
                    fraud_risk=u["suspicious_flag"],
                    anomaly_score=u["anomaly_score"]
                ) for u in data["users"]
            ]
            grouped_data.append(CategoryGroupedData(category=risk_level, count=data["count"], users=users))
        
        return OutputResponse(data=grouped_data, total_users=dashboard_data["total_users"])
    
    else:
        raise HTTPException(status_code=403, detail="Invalid role for this endpoint")

@app.get("/dashboard/analytics")
async def get_dashboard_analytics(
    category: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Legacy analytics endpoint - redirects to role-specific endpoints"""
    if current_user.role == "resident":
        # Get resident data
        pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == current_user.id).first()
        if not pension_data:
            raise HTTPException(status_code=404, detail="No pension data found")
        
        return {
            "role": "resident",
            "user_id": current_user.id,
            "analytics": {
                "pension_overview": {
                    "current_savings": pension_data.current_savings or 0,
                    "projected_amount": pension_data.projected_pension_amount or 0,
                    "annual_income": pension_data.annual_income or 0,
                    "contribution_rate": pension_data.contribution_amount or 0,
                    "years_to_retirement": max(0, (pension_data.retirement_age_goal or 65) - (pension_data.age or 0))
                },
                "risk_profile": {
                    "risk_tolerance": pension_data.risk_tolerance,
                    "volatility": pension_data.volatility or 0,
                    "portfolio_diversity": pension_data.portfolio_diversity_score or 0,
                    "debt_ratio": (pension_data.debt_level or 0) / (pension_data.annual_income or 1) if pension_data.annual_income else 0
                },
                "fraud_indicators": {
                    "anomaly_score": pension_data.anomaly_score or 0,
                    "suspicious_flag": pension_data.suspicious_flag,
                    "transaction_amount": pension_data.transaction_amount or 0,
                    "geo_location": pension_data.geo_location
                }
            }
        }
    
    elif current_user.role == "advisor":
        # Get advisor dashboard data
        dashboard_data = await get_advisor_dashboard(current_user, db)
        return {
            "role": "advisor",
            "analytics": dashboard_data,
            "total_clients": dashboard_data["total_clients"]
        }
    
    elif current_user.role == "regulator":
        # Get regulator dashboard data
        dashboard_data = await get_regulator_dashboard(current_user, db)
        return {
            "role": "regulator",
            "analytics": dashboard_data,
            "total_users": dashboard_data["total_users"]
        }
    
    else:
        raise HTTPException(status_code=403, detail="Invalid role for this endpoint")

# ---------------------------
# Utility Endpoints
# ---------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Pension AI API", "version": "1.0.0"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/users/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed dashboard data for a specific user"""
    # Check permissions
    if current_user.role == "resident" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Can only view own dashboard")
    
    if current_user.role == "advisor":
        # Check if user is a client of this advisor
        client_relationship = db.query(models.AdvisorClient).filter(
            models.AdvisorClient.advisor_id == current_user.id,
            models.AdvisorClient.resident_id == user_id
        ).first()
        if not client_relationship:
            raise HTTPException(status_code=403, detail="User not in your client list")
    
    # Get user data
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == user_id).first()
    if not pension_data:
        raise HTTPException(status_code=404, detail="No pension data found for this user")
    
    return {
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        },
        "pension_data": {
            "age": pension_data.age,
            "risk_tolerance": pension_data.risk_tolerance,
            "current_savings": pension_data.current_savings,
            "annual_income": pension_data.annual_income,
            "projected_pension_amount": pension_data.projected_pension_amount,
            "fraud_risk": pension_data.suspicious_flag,
            "anomaly_score": pension_data.anomaly_score,
            "portfolio_diversity_score": pension_data.portfolio_diversity_score,
            "volatility": pension_data.volatility
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)