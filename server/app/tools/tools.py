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
        return json.loads(response.content)
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
        return json.loads(response.content)
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
        annual_return_rate = pension_data.annual_return_rate or 0.08
        
        print(f"🔍 Tool Debug - Pension Type: {pension_type}")
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
                    print(f"🔍 Tool Debug - Capped projection from ₹{projected_balance:,.0f} to ₹{max_reasonable_projection:,.0f}")
                
                # Calculate scenarios with realistic limits
                scenario_10_percent = min(projected_balance * 1.1, max_reasonable_projection * 1.1)
                scenario_20_percent = min(projected_balance * 1.2, max_reasonable_projection * 1.2)
                
                print(f"🔍 Tool Debug - DC Calculation: FV Current=₹{fv_current:,.0f}, FV Contributions=₹{fv_contributions:,.0f}")
                print(f"🔍 Tool Debug - Projected Balance: ₹{projected_balance:,.0f}")
                
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
            print(f"🔍 Tool Debug - DB Plan: Using projected amount ₹{projected_balance:,.0f}")
            
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
            
            print(f"🔍 Tool Debug - Hybrid/Unknown: Conservative calculation ₹{projected_balance:,.0f}")
        
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
        
        # Format the response
        response = {
            "current_data": {
                "current_savings": f"₹{current_savings:,.0f}",
                "annual_income": f"₹{annual_income:,.0f}",
                "age": age,
                "retirement_age_goal": retirement_age_goal,
                "annual_contribution": f"₹{total_annual_contribution:,.0f}",
                "savings_rate": f"{savings_rate_percentage:.1f}%",
                "pension_type": pension_type
            },
            "projection_analysis": {
                "years_to_retirement": years_to_retirement,
                "projected_balance": f"₹{projected_balance:,.0f}",
                "scenario_10_percent_increase": f"₹{scenario_10_percent:,.0f}",
                "scenario_20_percent_increase": f"₹{scenario_20_percent:,.0f}",
                "annual_return_rate": f"{annual_return_rate * 100:.1f}%",
                "validation_warnings": validation_warnings,
                "calculation_notes": calculation_notes
            },
            "status": status,
            "progress_to_goal": f"{progress_percentage:.1f}%"
        }
        
        return response
        
    except Exception as e:
        print(f"🔍 Tool Error: {str(e)}")
        return {"error": f"Error processing pension projection: {str(e)}"}
    finally:
        db.close()

# --- Tool 4: Knowledge Base Search ---
class KnowledgeSearchInput(BaseModel):
    query: str = Field(description="The search query for the knowledge base.")
    user_id: Optional[int] = Field(description="The numeric database ID for the user. If not provided, will be retrieved from current session.")

@tool(args_schema=KnowledgeSearchInput)
def knowledge_base_search(query: str, user_id: int = None) -> Dict[str, Any]:
    """
    Searches the knowledge base for relevant information about pensions, retirement planning,
    and financial advice. Returns structured information based on the query.
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
    try:
        # Get or create the collection
        collection = get_or_create_collection("pension_knowledge")
        
        # Search the collection
        results = query_collection(collection, query, n_results=3)
        
        if not results or not results['documents']:
            return {
                "found": False,
                "message": "No relevant information found in the knowledge base.",
                "suggestions": [
                    "Try rephrasing your question",
                    "Use more specific terms",
                    "Check if your question is related to pensions, retirement, or financial planning"
                ]
            }
        
        # Format the results
        formatted_results = []
        for i, (doc, metadata, distance) in enumerate(zip(results['documents'], results['metadatas'], results['distances'])):
            formatted_results.append({
                "result": i + 1,
                "content": doc,
                "source": metadata.get('source', 'Unknown'),
                "relevance_score": 1 - distance  # Convert distance to similarity score
            })
        
        return {
            "found": True,
            "query": query,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "summary": f"Found {len(formatted_results)} relevant results for your query about '{query}'."
        }
        
    except Exception as e:
        return {"error": f"Error searching knowledge base: {str(e)}"}

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
    knowledge_base_search
]


