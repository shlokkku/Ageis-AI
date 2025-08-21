import json
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from langchain.tools import tool
from pydantic.v1 import BaseModel, Field, validator, root_validator
import re

from ..database import SessionLocal
from .. import models
from ..chromadb_service import get_or_create_collection, query_collection
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Set Google API key for LangChain with fallback
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    os.environ["GOOGLE_API_KEY"] = gemini_key
else:
    # Set a dummy key for testing (will fail gracefully)
    os.environ["GOOGLE_API_KEY"] = "dummy_key_for_testing"

json_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    response_mime_type="application/json"
)

# --- Tool 1: Risk Analysis ---
class RiskToolInput(BaseModel):
    user_id: Optional[int] = Field(description="The numeric database ID for the user. If not provided, will be retrieved from current session.")
    query: Optional[str] = Field(description="The user's original query for context")

    @validator("user_id", pre=True)
    def coerce_user_id(cls, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        return None

@tool(args_schema=RiskToolInput)
def analyze_risk_profile(user_id: int = None) -> Dict[str, Any]:
    """
    Analyzes a user's risk profile based on their ID by fetching their data
    and evaluating it against fixed financial risk factors.
    Returns a structured JSON object with the complete risk assessment.
    """
    # PRIORITY 1: Get user_id from request context (most secure)
    if user_id is None:
        user_id = get_current_user_id_from_context()
        if user_id:
            print(f"🔍 Context: Using user_id={user_id} from request context")
    
    # PRIORITY 2: Clean up the input if it's not a clean integer
    if user_id is None or isinstance(user_id, str):
        user_id = extract_user_id_from_input(user_id)
        if user_id:
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from input")
    
    if not user_id:
        return {"error": "User not authenticated. Please log in."}
    
    print(f"\n--- TOOL: Running Risk Analysis for User ID: {user_id} ---")
    db: Session = SessionLocal()
    try:
        pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == user_id).first()
        if not pension_data:
            return {"error": f"No pension data found for User ID: {user_id}"}

        user_data = {
            "Annual_Income": pension_data.annual_income,
            "Debt_Level": pension_data.debt_level,
            "Risk_Tolerance": pension_data.risk_tolerance,
            "Volatility": pension_data.volatility,
            "Portfolio_Diversity_Score": pension_data.portfolio_diversity_score,
            "Health_Status": pension_data.health_status
        }
        prompt = f"""
        **SYSTEM:** You are a Methodical Financial Risk Analyst System...
        **TASK:** Analyze the user's data below...
        **RISK ANALYSIS FACTORS:**
        1.  **Market Risk Mismatch**: `Risk_Tolerance` is 'Low' but `Volatility` > 3.5.
        2.  **Concentration Risk**: `Portfolio_Diversity_Score` < 0.5.
        3.  **High Debt-to-Income Ratio**: `Debt_Level` > 50% of `Annual_Income`.
        4.  **Longevity & Health Risk**: `Health_Status` is 'Poor'.
        **DATA TO ANALYZE:**
        ```json
        {json.dumps(user_data, indent=2)}
        ```
        **OUTPUT INSTRUCTIONS:**
        Return a single JSON object with this structure: {{"risk_level": "Low/Medium/High", "risk_score": float, "positive_factors": [], "risks_identified": [], "summary": "..."}}
        """
        response = json_llm.invoke(prompt)
        result = json.loads(response.content)
        
        # Add data source information
        result["data_source"] = "DATABASE_PENSION_DATA"
        result["note"] = "This risk analysis is based on your pension data stored in our database, not from uploaded documents."
        
        return result
    finally:
        db.close()

# --- Tool 2: Fraud Detection ---
class FraudToolInput(BaseModel):
    user_id: Optional[int] = Field(description="The numeric database ID for the user. If not provided, will be retrieved from current session.")
    query: Optional[str] = Field(description="The user's original query for context")

    @validator("user_id", pre=True)
    def coerce_user_id(cls, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        return None

@tool(args_schema=FraudToolInput)
def detect_fraud(user_id: int = None) -> Dict[str, Any]:
    """
    Analyzes a user's recent transactions based on their ID to detect potential fraud.
    Evaluates data against fixed rules and returns a structured JSON assessment.
    """
    # PRIORITY 1: Get user_id from request context (most secure)
    if user_id is None:
        user_id = get_current_user_id_from_context()
        if user_id:
            print(f"🔍 Context: Using user_id={user_id} from request context")
    
    # PRIORITY 2: Clean up the input if it's not a clean integer
    if user_id is None or isinstance(user_id, str):
        user_id = extract_user_id_from_input(user_id)
        if user_id:
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from input")
    
    if not user_id:
        return {"error": "User not authenticated. Please log in."}
    
    print(f"\n--- TOOL: Running Fraud Detection for User ID: {user_id} ---")
    db: Session = SessionLocal()
    try:
        pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == user_id).first()
        if not pension_data:
            return {"error": f"No pension data found for User ID: {user_id}"}
        
        user_data = {
            "Country": pension_data.country,
            "Transaction_Amount": pension_data.transaction_amount,
            "Suspicious_Flag": pension_data.suspicious_flag,
            "Anomaly_Score": pension_data.anomaly_score,
            "Geo_Location": pension_data.geo_location
        }
        
        prompt = f"""
        **SYSTEM:** You are a Financial Fraud Detection System...
        **TASK:** Analyze the user's transaction data below...
        **FRAUD DETECTION FACTORS:**
        1.  **Geographic Anomaly**: `Geo_Location` doesn't match `Country`.
        2.  **Suspicious Amount**: `Transaction_Amount` is unusually high/low.
        3.  **Flagged Transaction**: `Suspicious_Flag` is True.
        4.  **High Anomaly Score**: `Anomaly_Score` > 0.8.
        **DATA TO ANALYZE:**
        ```json
        {json.dumps(user_data, indent=2)}
        ```
        **OUTPUT INSTRUCTIONS:**
        Return a single JSON object with this structure: {{"fraud_risk": "Low/Medium/High", "fraud_score": float, "suspicious_factors": [], "recommendations": [], "summary": "..."}}
        """
        response = json_llm.invoke(prompt)
        result = json.loads(response.content)
        
        # Add data source information
        result["data_source"] = "DATABASE_PENSION_DATA"
        result["note"] = "This fraud detection analysis is based on your pension data stored in our database, not from uploaded documents."
        
        return result
    finally:
        db.close()

# --- Tool 3: Pension Projection ---
class ProjectionToolInput(BaseModel):
    user_id: Optional[int] = Field(description="The numeric database ID for the user. If not provided, will be retrieved from current session.")
    query: Optional[str] = Field(description="The user's original query to parse time periods from (e.g., 'retire in 3 years')")

    @validator("user_id", pre=True)
    def coerce_user_id(cls, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        return None

def parse_time_period_from_query(query: str, current_age: int, retirement_age: int) -> int:
    """
    Parse natural language queries to extract the time period for pension calculations.
    Returns the number of years to use in calculations.
    """
    query_lower = query.lower()
    
    # Pattern 1: "retire in X years"
    match = re.search(r'retire\s+in\s+(\d+)\s+years?', query_lower)
    if match:
        years = int(match.group(1))
        print(f"🔍 Time Parsing: Found 'retire in {years} years' → Using {years} years")
        return years
    
    # Pattern 2: "retire at age X"
    match = re.search(r'retire\s+at\s+age\s+(\d+)', query_lower)
    if match:
        target_age = int(match.group(1))
        years = max(0, target_age - current_age)
        print(f"🔍 Time Parsing: Found 'retire at age {target_age}' → Using {years} years")
        return years
    
    # Pattern 3: "retire early" or "retire soon"
    if 'retire early' in query_lower or 'retire soon' in query_lower:
        years = min(5, retirement_age - current_age)  # Assume 5 years or less
        print(f"🔍 Time Parsing: Found 'retire early/soon' → Using {years} years")
        return years
    
    # Pattern 4: "retire next year"
    if 'retire next year' in query_lower:
        years = 1
        print(f"🔍 Time Parsing: Found 'retire next year' → Using {years} years")
        return years
    
    # Pattern 5: "retire in X months"
    match = re.search(r'retire\s+in\s+(\d+)\s+months?', query_lower)
    if match:
        months = int(match.group(1))
        years = months / 12
        print(f"🔍 Time Parsing: Found 'retire in {months} months' → Using {years:.1f} years")
        return max(0.1, years)  # Minimum 0.1 years
    
    # Default: Use full retirement age
    default_years = retirement_age - current_age
    print(f"🔍 Time Parsing: No specific time found → Using default {default_years} years to retirement")
    return default_years

@tool(args_schema=ProjectionToolInput)
def project_pension(user_id: int = None, query: str = None) -> Dict[str, Any]:
    """
    Provides a comprehensive pension overview including current savings, goal progress,
    years remaining, savings rate, and projected balance at retirement.
    Can also calculate specific time-based projections based on the query.
    """
    # PRIORITY 1: Get user_id from tool input (most direct)
    if user_id is None:
        # Try to get from context as fallback
        user_id = get_current_user_id_from_context()
        if user_id:
            print(f"🔍 Context: Using user_id={user_id} from request context")
    
    # PRIORITY 2: Clean up the input if it's not a clean integer
    if user_id is None or isinstance(user_id, str):
        user_id = extract_user_id_from_input(user_id)
        if user_id:
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from input")
    
    if not user_id:
        return {"error": "User not authenticated. Please log in."}
    
    print(f"🔍 Tool Debug - User ID: {user_id}, Query: {query}")
    
    db: Session = SessionLocal()
    try:
        pension_data = db.query(models.PensionData).filter(models.PensionData.user_id == user_id).first()
        if not pension_data:
            return {"error": f"No pension data found for User ID: {user_id}"}
        
        # Extract all pension data fields
        current_savings = pension_data.current_savings or 0
        annual_income = pension_data.annual_income or 0
        age = pension_data.age or 0
        retirement_age_goal = pension_data.retirement_age_goal or 65
        annual_contribution = pension_data.contribution_amount or 0
        employer_contribution = pension_data.employer_contribution or 0
        total_annual_contribution = annual_contribution + employer_contribution
        pension_type = pension_data.pension_type or "Defined Contribution"
        # Normalize return rate to ensure it's in decimal format (e.g., 6.88% -> 0.0688)
        raw_return_rate = pension_data.annual_return_rate or 0.08
        if raw_return_rate > 1.0:  # If it's greater than 100%, convert from percentage
            annual_return_rate = raw_return_rate / 100.0
        else:
            annual_return_rate = raw_return_rate
        
        print(f"🔍 Tool Debug - Pension Type: {pension_type}")
        print(f"🔍 Tool Debug - Raw Return Rate: {raw_return_rate}")
        print(f"🔍 Tool Debug - Normalized Return Rate: {annual_return_rate}")
        print(f"🔍 Tool Debug - Current Savings: {current_savings}")
        print(f"🔍 Tool Debug - Annual Income: {annual_income}")
        print(f"🔍 Tool Debug - Age: {age}")
        print(f"🔍 Tool Debug - Retirement Goal: {retirement_age_goal}")
        
        # Parse time period from query if provided
        if query:
            years_to_retirement = parse_time_period_from_query(query, age, retirement_age_goal)
        else:
            years_to_retirement = max(0, retirement_age_goal - age)
        
        print(f"🔍 Tool Debug - Years to Retirement: {years_to_retirement}")
        
        # Calculate retirement goal (example: 10x annual income)
        retirement_goal_amount = annual_income * 10
        
        # Calculate progress
        progress_percentage = min(100, (current_savings / retirement_goal_amount) * 100) if retirement_goal_amount > 0 else 0
        
        # Determine status
        if age >= retirement_age_goal:
            status = "At Retirement Age"
        elif progress_percentage >= 80:
            status = "On Track"
        elif progress_percentage >= 50:
            status = "Good Progress"
        else:
            status = "Needs Attention"
        
        # Calculate savings rate
        savings_rate_percentage = (total_annual_contribution / annual_income) * 100 if annual_income > 0 else 0
        
        # Calculate projections based on pension type with realistic limits
        if pension_type.lower() in ["defined contribution", "dc", "defined contribution plan"]:
            # DEFINED CONTRIBUTION: Future value based on contributions + investment returns
            if years_to_retirement > 0:
                # Use more conservative return rate for longer periods
                if years_to_retirement > 20:
                    effective_return_rate = min(annual_return_rate, 0.06)  # Cap at 6% for very long periods
                elif years_to_retirement > 10:
                    effective_return_rate = min(annual_return_rate, 0.07)  # Cap at 7% for long periods
                else:
                    effective_return_rate = annual_return_rate
                
                # Future value of current savings
                fv_current = current_savings * (1 + effective_return_rate) ** years_to_retirement
                
                # Future value of contributions (more conservative)
                if total_annual_contribution > 0:
                    fv_contributions = total_annual_contribution * ((1 + effective_return_rate) ** years_to_retirement - 1) / effective_return_rate
                else:
                    fv_contributions = 0
                
                projected_balance = fv_current + fv_contributions
                
                # Apply realistic limits to prevent impossible projections
                max_reasonable_multiplier = min(10, years_to_retirement * 0.5)  # More conservative
                max_reasonable_projection = current_savings * max_reasonable_multiplier
                
                if projected_balance > max_reasonable_projection:
                    projected_balance = max_reasonable_projection
                    print(f"🔍 Tool Debug - Capped projection from £{projected_balance:,.0f} to £{max_reasonable_projection:,.0f}")
                
                # Calculate scenarios with realistic limits
                scenario_10_percent = min(projected_balance * 1.1, max_reasonable_projection * 1.1)
                scenario_20_percent = min(projected_balance * 1.2, max_reasonable_projection * 1.2)
                
                print(f"🔍 Tool Debug - DC Calculation: FV Current=£{fv_current:,.0f}, FV Contributions=£{fv_contributions:,.0f}")
                print(f"🔍 Tool Debug - Projected Balance: £{projected_balance:,.0f}")
                
            else:
                projected_balance = current_savings
                scenario_10_percent = current_savings
                scenario_20_percent = current_savings
                
        elif pension_type.lower() in ["defined benefit", "db", "defined benefit plan"]:
            # DEFINED BENEFIT: Pension based on salary, years of service, and benefit formula
            # For DB plans, contributions don't directly affect the benefit
            projected_balance = pension_data.projected_pension_amount or (annual_income * 0.6)  # 60% of final salary
            scenario_10_percent = projected_balance
            scenario_20_percent = projected_balance
            print(f"🔍 Tool Debug - DB Plan: Using projected amount £{projected_balance:,.0f}")
            
        else:
            # HYBRID or UNKNOWN: Use a conservative approach
            if years_to_retirement > 0:
                # More conservative return rate
                conservative_return = min(annual_return_rate * 0.8, 0.06)  # 80% of original rate, max 6%
                projected_balance = current_savings * (1 + conservative_return) ** years_to_retirement
                
                # Apply realistic limits
                max_reasonable = current_savings * min(8, years_to_retirement * 0.4)
                if projected_balance > max_reasonable:
                    projected_balance = max_reasonable
                
                scenario_10_percent = min(projected_balance * 1.1, max_reasonable * 1.1)
                scenario_20_percent = min(projected_balance * 1.2, max_reasonable * 1.2)
            else:
                projected_balance = current_savings
                scenario_10_percent = current_savings
                scenario_20_percent = current_savings
            
            print(f"🔍 Tool Debug - Hybrid/Unknown: Conservative calculation £{projected_balance:,.0f}")
        
        # Validation and warnings
        validation_warnings = []
        calculation_notes = []
        
        # Check for unrealistic projections
        if projected_balance > current_savings * 20:
            validation_warnings.append("Projection may be optimistic - consider reviewing assumptions")
            calculation_notes.append("Large projection due to long time horizon or high return assumptions")
        
        if years_to_retirement < 1:
            calculation_notes.append("User is at or past retirement age - projection shows current status")
        
        # Additional validation for very short time periods
        if years_to_retirement <= 3 and projected_balance > current_savings * 2:
            validation_warnings.append("Short-term projection seems high - consider more conservative estimates")
            calculation_notes.append("Short time periods typically show smaller growth")
        
        # Generate chart data for visualizations
        chart_data = {}
        
        # Chart 1: Pension Growth Over Time
        if years_to_retirement > 0:
            years_data = list(range(age, retirement_age_goal + 1))
            projected_values = []
            for year in years_data:
                years_from_now = year - age
                if years_from_now <= 0:
                    projected_values.append(current_savings)
                else:
                    # Calculate projected value for this year
                    fv_current = current_savings * (1 + annual_return_rate) ** years_from_now
                    if total_annual_contribution > 0:
                        fv_contributions = total_annual_contribution * ((1 + annual_return_rate) ** years_from_now - 1) / annual_return_rate
                    else:
                        fv_contributions = 0
                    projected_values.append(min(fv_current + fv_contributions, current_savings * 20))  # Cap at 20x
            
            chart_data["pension_growth"] = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "description": "Pension growth projection over time",
                "data": {
                    "values": [{"age": y, "projected_value": v} for y, v in zip(years_data, projected_values)]
                },
                "mark": "line",
                "encoding": {
                    "x": {
                        "field": "age",
                        "type": "quantitative",
                        "title": "Age"
                    },
                    "y": {
                        "field": "projected_value",
                        "type": "quantitative",
                        "title": "Projected Pension Value (£)"
                    }
                }
            }
        
        # Chart 2: Progress to Goal
        chart_data["progress_to_goal"] = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Progress toward retirement goal",
            "data": {
                "values": [
                    {"metric": "Current Savings", "value": current_savings},
                    {"metric": "Goal Amount", "value": retirement_goal_amount}
                ]
            },
            "mark": "bar",
            "encoding": {
                "x": {
                    "field": "metric",
                    "type": "nominal",
                    "title": ""
                },
                "y": {
                    "field": "value",
                    "type": "quantitative",
                    "title": "Amount (£)"
                }
            }
        }
        
        # Chart 3: Savings Rate Analysis
        chart_data["savings_analysis"] = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Savings rate and contribution analysis",
            "data": {
                "values": [
                    {"category": "Annual Income", "amount": annual_income},
                    {"category": "Annual Contribution", "amount": total_annual_contribution},
                    {"category": "Current Savings", "amount": current_savings}
                ]
            },
            "mark": "bar",
            "encoding": {
                "x": {
                    "field": "category",
                    "type": "nominal",
                    "title": ""
                },
                "y": {
                    "field": "amount",
                    "type": "quantitative",
                    "title": "Amount (£)"
                }
            }
        }
        
        # Format the response
        response = {
            "current_data": {
                "current_savings": f"£{current_savings:,.0f}",
                "annual_income": f"£{annual_income:,.0f}",
                "age": age,
                "retirement_age_goal": retirement_age_goal,
                "annual_contribution": f"£{total_annual_contribution:,.0f}",
                "savings_rate": f"{savings_rate_percentage:.1f}%",
                "pension_type": pension_type
            },
            "projection_analysis": {
                "years_to_retirement": years_to_retirement,
                "projected_balance": f"£{projected_balance:,.0f}",
                "scenario_10_percent_increase": f"£{scenario_10_percent:,.0f}",
                "scenario_20_percent_increase": f"£{scenario_20_percent:,.0f}",
                "annual_return_rate": f"{annual_return_rate * 100:.1f}%",
                "validation_warnings": validation_warnings,
                "calculation_notes": calculation_notes
            },
            "status": status,
            "progress_to_goal": f"{progress_percentage:.1f}%",
            "chart_data": chart_data,
            "data_source": "DATABASE_PENSION_DATA",
            "note": "This analysis is based on your pension data stored in our database, not from uploaded documents."
        }
        
        return response
        
    except Exception as e:
        print(f"🔍 Tool Error: {str(e)}")
        return {"error": f"Error processing pension projection: {str(e)}"}
    finally:
        db.close()

# --- Tool 4: Knowledge Base Search (Enhanced) ---
class KnowledgeSearchInput(BaseModel):
    query: str = Field(description="The search query for the knowledge base.")
    user_id: Optional[int] = Field(description="The numeric database ID for the user. If not provided, will be retrieved from current session.")

    @validator("user_id", pre=True)
    def coerce_user_id(cls, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        return None

@tool(args_schema=KnowledgeSearchInput)
def knowledge_base_search(query: str, user_id: int = None) -> Dict[str, Any]:
    """
    Searches the knowledge base for relevant information about pensions, retirement planning,
    and financial advice. Returns structured information based on the query.
    This tool searches BOTH general pension knowledge AND the user's uploaded documents.
    """
    # PRIORITY 1: Get user_id from request context (most secure)
    if user_id is None:
        user_id = get_current_user_id_from_context()
        if user_id:
            print(f"🔍 Context: Using user_id={user_id} from request context")
    
    # PRIORITY 2: Clean up the input if it's not a clean integer
    if user_id is None or isinstance(user_id, str):
        user_id = extract_user_id_from_input(user_id)
        if user_id:
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from input")
    
    if not user_id:
        return {"error": "User not authenticated. Please log in."}
    
    print(f"\n--- TOOL: Searching Knowledge Base for User ID: {user_id} ---")
    
    all_results = []
    
    try:
        # SEARCH 1: General pension knowledge base
        print(f"🔍 Searching general pension knowledge base...")
        general_collection = get_or_create_collection("pension_knowledge")
        general_results = query_collection(general_collection, [query], n_results=2)
        
        # Handle ChromaDB results properly
        if general_results and isinstance(general_results, dict) and 'documents' in general_results:
            general_docs = general_results.get('documents', [])
            general_metadatas = general_results.get('metadatas', [])
            general_distances = general_results.get('distances', [])
            
            # ChromaDB returns nested lists, flatten them
            if general_docs and isinstance(general_docs[0], list):
                general_docs = general_docs[0]
            if general_metadatas and isinstance(general_metadatas[0], list):
                general_metadatas = general_metadatas[0]
            if general_distances and isinstance(general_distances[0], list):
                general_distances = general_distances[0]
            
            for i, (doc, metadata, distance) in enumerate(zip(general_docs, general_metadatas, general_distances)):
                if doc:  # Only add if document content exists
                    all_results.append({
                        "result": len(all_results) + 1,
                        "content": doc,
                        "source": "General Pension Knowledge Base",
                        "type": "general_knowledge",
                        "relevance_score": 1 - distance if isinstance(distance, (int, float)) else 0.5
                    })
        
        # SEARCH 2: User's uploaded PDF documents
        print(f"🔍 Searching user's uploaded documents...")
        user_docs_collection = get_or_create_collection(f"user_{user_id}_docs")
        user_results = query_collection(user_docs_collection, [query], n_results=3)
        
        # Handle ChromaDB results properly
        if user_results:
            if isinstance(user_results, dict) and 'documents' in user_results:
                user_docs = user_results.get('documents', [])
                user_metadatas = user_results.get('metadatas', [])
                user_distances = user_results.get('distances', [])
                
                # ChromaDB returns nested lists, flatten them
                if user_docs and isinstance(user_docs[0], list):
                    user_docs = user_docs[0]
                if user_metadatas and isinstance(user_metadatas[0], list):
                    user_metadatas = user_metadatas[0]
                if user_distances and isinstance(user_distances[0], list):
                    user_distances = user_distances[0]
                    
            elif isinstance(user_results, list):
                # If it's a list, assume it's the documents directly
                user_docs = user_results
                user_metadatas = [{}] * len(user_results)
                user_distances = [0.0] * len(user_results)
            else:
                user_docs = []
                user_metadatas = []
                user_distances = []
            
            for i, (doc, metadata, distance) in enumerate(zip(user_docs, user_metadatas, user_distances)):
                if doc:  # Only add if document content exists
                    # Handle distance calculation safely
                    try:
                        if isinstance(distance, (int, float)):
                            relevance_score = 1 - distance
                        elif isinstance(distance, list) and len(distance) > 0:
                            first_distance = distance[0]
                            if isinstance(first_distance, (int, float)):
                                relevance_score = 1 - first_distance
                            else:
                                relevance_score = 0.5
                        else:
                            relevance_score = 0.5
                    except (TypeError, ValueError):
                        relevance_score = 0.5
                    
                    all_results.append({
                        "result": len(all_results) + 1,
                        "content": doc,
                        "source": metadata.get('source', f'User {user_id} Document') if metadata else f'User {user_id} Document',
                        "type": "user_document",
                        "relevance_score": relevance_score
                    })
        
        # If no results found anywhere
        if not all_results:
            return {
                "found": False,
                "message": "No relevant information found in either the general knowledge base or your uploaded documents.",
                "suggestions": [
                    "Try rephrasing your question",
                    "Use more specific terms",
                    "Check if your question is related to pensions, retirement, or financial planning",
                    "Make sure you have uploaded relevant documents"
                ]
            }
        
        # Sort results by relevance score
        all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Update result numbers after sorting
        for i, result in enumerate(all_results):
            result["result"] = i + 1
        
        return {
            "found": True,
            "query": query,
            "results": all_results,
            "total_results": len(all_results),
            "search_summary": {
                "general_knowledge_results": len([r for r in all_results if r.get('type') == 'general_knowledge']),
                "user_document_results": len([r for r in all_results if r.get('type') == 'user_document']),
                "total_found": len(all_results)
            },
            "summary": f"Found {len(all_results)} relevant results for your query about '{query}'. "
                      f"This includes both general pension knowledge and information from your uploaded documents."
        }
        
    except Exception as e:
        return {"error": f"Error searching knowledge base: {str(e)}"}

# --- Tool 5: Document Analysis ---
class DocumentAnalysisInput(BaseModel):
    query: str = Field(description="The question or query about the uploaded document")
    user_id: Optional[int] = Field(description="User ID to identify which documents to search. If not provided, will be retrieved from context.")

@tool(args_schema=DocumentAnalysisInput)
def analyze_uploaded_document(query: str, user_id: int = None) -> Dict[str, Any]:
    """
    Analyzes the user's uploaded PDF documents to answer specific questions.
    This tool searches through all documents uploaded by the user and provides
    relevant information based on the query.
    """
    # PRIORITY 1: Get user_id from request context (most secure)
    if user_id is None:
        user_id = get_current_user_id_from_context()
        if user_id:
            print(f"🔍 Context: Using user_id={user_id} from request context")
    
    # PRIORITY 2: Clean up the input if it's not a clean integer
    if user_id is None or isinstance(user_id, str):
        user_id = extract_user_id_from_input(user_id)
        if user_id:
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from input")
    
    if not user_id:
        return {"error": "User not authenticated. Please log in."}
    
    print(f"\n--- TOOL: Analyzing Uploaded Documents for User ID: {user_id} ---")
    
    try:
        # Search user's uploaded documents
        user_docs_collection = get_or_create_collection(f"user_{user_id}_docs")
        user_results = query_collection(user_docs_collection, [query], n_results=5)
        
        # ChromaDB returns results in different formats, handle both
        if isinstance(user_results, dict):
            user_docs = user_results.get('documents', [])
            user_metadatas = user_results.get('metadatas', [])
            user_distances = user_results.get('distances', [])
            
            # ChromaDB returns nested lists, flatten them
            if user_docs and isinstance(user_docs[0], list):
                user_docs = user_docs[0]
            if user_metadatas and isinstance(user_metadatas[0], list):
                user_metadatas = user_metadatas[0]
            if user_distances and isinstance(user_distances[0], list):
                user_distances = user_distances[0]
                
        elif isinstance(user_results, list):
            # If it's a list, assume it's the documents directly
            user_docs = user_results
            user_metadatas = [{}] * len(user_results)
            user_distances = [0.0] * len(user_results)
        else:
            return {
                "found": False,
                "message": f"Unexpected result format from document search: {type(user_results)}",
                "suggestions": ["Try again or contact support"]
            }
        
        if not user_docs:
            return {
                "found": False,
                "message": "No uploaded documents found for analysis.",
                "suggestions": [
                    "Upload a PDF document first using the upload endpoint",
                    "Check if your document was successfully processed",
                    "Try a different query related to your uploaded content"
                ]
            }
        
        # Format the results
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(user_docs, user_metadatas, user_distances)):
            if doc:  # Only add if document content exists
                # Handle distance calculation safely
                try:
                    if isinstance(distance, (int, float)):
                        relevance_score = 1 - distance
                    elif isinstance(distance, list) and len(distance) > 0:
                        first_distance = distance[0]
                        if isinstance(first_distance, (int, float)):
                            relevance_score = 1 - first_distance
                        else:
                            relevance_score = 0.5
                    else:
                        relevance_score = 0.5
                except (TypeError, ValueError):
                    relevance_score = 0.5
                
                formatted_results.append({
                    "result": i + 1,
                    "content": doc,
                    "source": metadata.get('source', f'User {user_id} Document') if metadata else f'User {user_id} Document',
                    "relevance_score": relevance_score,
                    "analysis": f"Document chunk {i+1} contains relevant information for your query: '{query}'"
                })
        
        # Sort by relevance
        formatted_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Update result numbers after sorting
        for i, result in enumerate(formatted_results):
            result["result"] = i + 1
        
        return {
            "found": True,
            "query": query,
            "document_analysis": True,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "summary": f"Successfully analyzed your uploaded documents for '{query}'. "
                      f"Found {len(formatted_results)} relevant document sections.",
            "capabilities": [
                "Search through all your uploaded PDF documents",
                "Extract relevant information based on your questions",
                "Provide context-aware answers from your documents",
                "Support for multiple document types and formats"
            ]
        }
        
    except Exception as e:
        return {"error": f"Error analyzing uploaded documents: {str(e)}"}

# --- Tool 6: Enhanced PDF Document Search ---
class PDFSearchInput(BaseModel):
    query: str = Field(description="The search query for the PDF documents.")
    user_id: Optional[int] = Field(description="The numeric database ID for the user. If not provided, will be retrieved from current session.")

    @validator("user_id", pre=True)
    def coerce_user_id(cls, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                return int(match.group(0))
        return None

@tool(args_schema=PDFSearchInput)
def query_knowledge_base(query: str, user_id: int = None) -> Dict[str, Any]:
    """
    Searches the user's uploaded PDF documents and knowledge base for relevant information.
    Returns structured information based on the query.
    """
    # PRIORITY 1: Get user_id from tool input (most direct)
    if user_id is None:
        # Try to get from context as fallback
        user_id = get_current_user_id_from_context()
        if user_id:
            print(f"🔍 Context: Using user_id={user_id} from request context")
    
    # PRIORITY 2: Clean up the input if it's not a clean integer
    if user_id is None or isinstance(user_id, str):
        user_id = extract_user_id_from_input(user_id)
        if user_id:
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from input")
    
    if not user_id:
        return {"error": "User not authenticated. Please log in."}
    
    print(f"\n--- TOOL: Searching Knowledge Base for User ID: {user_id} ---")
    
    # 🔍 FIX: Extract actual query from JSON input if needed
    actual_query = query
    if query.startswith('{') and query.endswith('}'):
        try:
            import json
            query_data = json.loads(query)
            if 'query' in query_data:
                actual_query = query_data['query']
                print(f"🔍 Fixed: Extracted actual query: '{actual_query}' from JSON input")
        except:
            print(f"🔍 Warning: Could not parse JSON input, using as-is")
    
    try:
        # Get the user's document collection
        collection_name = f"user_{user_id}_docs"
        collection = get_or_create_collection(collection_name)
        
        # 🔍 DEBUG: Check what we're passing to query_collection
        print(f"🔍 Debug: actual_query = '{actual_query}' (type: {type(actual_query)})")
        print(f"🔍 Debug: user_id = {user_id} (type: {type(user_id)})")
        
        # Search the collection - ensure query is a string
        if isinstance(actual_query, str):
            query_texts = [actual_query]
        elif isinstance(actual_query, list):
            query_texts = actual_query
        else:
            query_texts = [str(actual_query)]
        
        print(f"🔍 Debug: query_texts = {query_texts}")
        
        results = query_collection(collection, query_texts, n_results=3)
        
        # 🔍 DEBUG: Check what results we got back
        print(f"🔍 Debug: results type = {type(results)}")
        print(f"🔍 Debug: results keys = {list(results.keys()) if isinstance(results, dict) else 'Not a dict'}")
        
        if not results or not isinstance(results, dict) or not results.get('documents'):
            return {
                "found": False,
                "message": "No relevant information found in your uploaded documents.",
                "suggestions": [
                    "Try rephrasing your question",
                    "Use more specific terms",
                    "Check if you have uploaded relevant PDF documents",
                    "Make sure your question is related to pension, retirement, or financial planning"
                ],
                "user_id": user_id,
                "query": actual_query,
                "search_type": "PDF_DOCUMENT_SEARCH",
                "pdf_status": "NO_PDFS_FOUND",
                "note": "This response is from searching your uploaded PDF documents. No relevant documents were found for your query."
            }
        
        # Format the results
        formatted_results = []
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        distances = results.get('distances', [])
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # 🔍 FIX: Handle OCR placeholder content gracefully
            content = doc
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            
            # Check if content is just OCR placeholder
            if 'OCR processing required' in str(content) or 'Scanned content detected' in str(content):
                content = "This document appears to be scanned images. The content is not searchable as text. Please upload a text-based PDF or contact support for OCR processing."
            
            formatted_results.append({
                "result": i + 1,
                "content": content,
                "source": metadata.get('source', 'Unknown PDF') if isinstance(metadata, dict) else 'Unknown PDF',
                "relevance_score": round(1 - distance, 3) if isinstance(distance, (int, float)) else 0.0,
                "chunk_index": metadata.get('chunk_index', 'Unknown') if isinstance(metadata, dict) else 'Unknown'
            })
        
        return {
            "found": True,
            "query": actual_query,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "summary": f"Found {len(formatted_results)} relevant sections from your uploaded documents for your query about '{actual_query}'.",
            "user_id": user_id,
            "search_scope": f"User {user_id}'s PDF documents",
            "search_type": "PDF_DOCUMENT_SEARCH",
            "pdf_status": "PDFS_FOUND_AND_SEARCHED",
            "note": "This response is based on content extracted from your uploaded PDF documents.",
            "recommendations": [
                "The information above is extracted from your uploaded PDF documents",
                "For the most accurate answers, refer to the original document sources",
                "Consider consulting with a financial advisor for personalized advice"
            ]
        }
        
    except Exception as e:
        print(f"❌ Error searching knowledge base: {e}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        return {
            "error": f"Error searching knowledge base: {str(e)}",
            "user_id": user_id,
            "query": actual_query,
            "search_type": "PDF_DOCUMENT_SEARCH",
            "pdf_status": "ERROR_OCCURRED",
            "note": "An error occurred while searching your PDF documents."
        }

# Global context variable for user_id (shared across the module)
import contextvars
_user_id_context = contextvars.ContextVar('user_id', default=None)

# Fallback global variable for when context doesn't work
_current_user_id = None

# Helper function to get user_id from context
def get_current_user_id_from_context() -> Optional[int]:
    """
    Get user_id from current request context.
    This should be implemented based on your authentication system.
    """
    try:
        print(f"🔍 Context Debug: Attempting to get user_id from context...")
        
        # Option 1: Request-scoped context (production-ready)
        current_user_id = _user_id_context.get()
        print(f"🔍 Context Debug: Request context value: {current_user_id}")
        
        if current_user_id is not None:
            print(f"🔍 Context: Retrieved user_id={current_user_id} from request context")
            return current_user_id
        
        # Option 2: Global fallback variable
        if _current_user_id is not None:
            print(f"🔍 Context: Retrieved user_id={_current_user_id} from global fallback")
            return _current_user_id
        
        # Option 3: Thread-local storage (fallback for testing)
        import threading
        user_id = getattr(threading.current_thread(), 'user_id', None)
        print(f"🔍 Context Debug: Thread context value: {user_id}")
        
        if user_id is not None:
            print(f"🔍 Context: Retrieved user_id={user_id} from thread context (testing)")
            return user_id
        
        print(f"🔍 Context: No user_id found in context")
        return None
        
    except Exception as e:
        print(f"Error getting user_id from context: {e}")
        return None

def set_request_user_id(user_id: int):
    """
    Set the current user_id for the current request context.
    This is what your FastAPI endpoint should call.
    """
    try:
        global _current_user_id
        _current_user_id = user_id  # Set global fallback
        _user_id_context.set(user_id)
        print(f"🔍 Context: Set user_id={user_id} in request context and global fallback")
    except Exception as e:
        print(f"Error setting user_id in request context: {e}")
        # Fallback to thread-local for testing
        set_current_user_id(user_id)

def clear_request_user_id():
    """
    Clear the current user_id from the request context.
    This should be called at the end of each request.
    """
    try:
        global _current_user_id
        _current_user_id = None  # Clear global fallback
        _user_id_context.set(None)
        print(f"🔍 Context: Cleared user_id from request context and global fallback")
    except Exception as e:
        print(f"Error clearing user_id from request context: {e}")
        # Fallback to thread-local for testing
        clear_current_user_id()

def extract_user_id_from_input(input_value) -> Optional[int]:
    """
    Extract user_id from various input formats and clean them up
    """
    if input_value is None:
        return None
    
    # If it's already an integer, return it
    if isinstance(input_value, int):
        return input_value
    
    # If it's a string, try to extract the number
    if isinstance(input_value, str):
        # Remove common prefixes and extract just the number
        import re
        match = re.search(r'(\d+)', input_value)
        if match:
            user_id = int(match.group(1))
            print(f"🔍 Input Cleanup: Extracted user_id={user_id} from '{input_value}'")
            return user_id
    
    # If it's a dict, try to get user_id
    if isinstance(input_value, dict):
        user_id = input_value.get('user_id')
        if user_id:
            return extract_user_id_from_input(user_id)
    
    print(f"🔍 Input Cleanup: Could not extract user_id from '{input_value}'")
    return None

# Context manager for setting user_id during testing
import threading

def set_current_user_id(user_id: int):
    """Set the current user_id for the current thread (for testing)"""
    threading.current_thread().user_id = user_id

def clear_current_user_id():
    """Clear the current user_id for the current thread"""
    if hasattr(threading.current_thread(), 'user_id'):
        delattr(threading.current_thread(), 'user_id')

# Export all tools
all_pension_tools = [
    analyze_risk_profile,
    detect_fraud,
    project_pension,
    knowledge_base_search,
    analyze_uploaded_document,
    query_knowledge_base
]

