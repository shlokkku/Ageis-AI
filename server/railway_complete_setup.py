#!/usr/bin/env python3
"""
Complete Railway Database Setup Script (MySQL Version)
This script will:
1. Create all database tables
2. Import pension data from Excel
3. Create advisor and regulator users
4. Assign residents to advisors
5. Set all passwords to 'password-123'

Run this after setting DATABASE_URL environment variable on Railway
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, PensionData, AdvisorClient
from app.security import hash_password

def setup_railway_database():
    """Complete Railway database setup in one script"""
    
    # Get Railway database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not found!")
        print("Please set DATABASE_URL in your Railway environment variables")
        return
    
    # Configure your Excel file path here
    # Option 1: Hardcoded path (update this to your actual path)
    EXCEL_FILE_PATH = r"C:\Users\marya\OneDrive\Desktop\pension_data.xlsx"
    # Option 2: Environment variable (uncomment if you prefer)
    # EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH", r"C:\Users\marya\path\to\your\pension_data.xlsx")
    
    print("🚀 Starting Railway database setup...")
    
    # Create engine and tables
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Step 1: Create all tables
    print("\n📋 Step 1: Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
    db = SessionLocal()
    try:
        # Step 2: Import pension data from Excel
        print("\n📋 Step 2: Importing pension data...")
        try:
            # Use the configured file path
            EXCEL_FILE = EXCEL_FILE_PATH
            df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
            df.fillna("", inplace=True)
            
            users_created = 0
            pension_records_created = 0
            
            for idx, row in df.iterrows():
                user_id_value = str(row.get("User_ID")).strip()
                if not user_id_value:
                    continue

                user_email = f"{user_id_value}@example.com"
                
                # Create or get user
                user = db.query(User).filter(User.email == user_email).first()
                if not user:
                    user = User(
                        full_name=user_id_value,
                        email=user_email,
                        password=hash_password("password-123"),
                        role="resident"
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    users_created += 1

                # Clean transaction_date
                transaction_date_str = str(row.get("Transaction_Date")).strip()
                if transaction_date_str in ["", "########"]:
                    transaction_date = None
                else:
                    try:
                        transaction_date = pd.to_datetime(transaction_date_str)
                    except Exception:
                        transaction_date = None

                # Clean time_of_transaction
                time_of_transaction_str = str(row.get("Time_of_Transaction")).strip()
                if time_of_transaction_str in ["", "########"]:
                    time_of_transaction = None
                else:
                    try:
                        pd_time = pd.to_datetime(time_of_transaction_str, errors='coerce')
                        if pd_time is pd.NaT or len(time_of_transaction_str.split(":")) == 3 and len(time_of_transaction_str.split(" ")) == 1:
                            time_of_transaction = None
                        else:
                            time_of_transaction = pd_time
                    except Exception:
                        time_of_transaction = None

                # Create pension data
                pension = PensionData(
                    user_id=user.id,
                    age=int(row.get("Age") or 0),
                    gender=row.get("Gender"),
                    country=row.get("Country"),
                    employment_status=row.get("Employment_Status"),
                    annual_income=float(row.get("Annual_Income") or 0.0),
                    current_savings=float(row.get("Current_Savings") or 0.0),
                    retirement_age_goal=int(row.get("Retirement_Age_Goal") or 0),
                    risk_tolerance=row.get("Risk_Tolerance"),
                    contribution_amount=float(row.get("Contribution_Amount") or 0.0),
                    contribution_frequency=row.get("Contribution_Frequency"),
                    employer_contribution=float(row.get("Employer_Contribution") or 0.0),
                    total_annual_contribution=float(row.get("Total_Annual_Contribution") or 0.0),
                    years_contributed=int(row.get("Years_Contributed") or 0),
                    investment_type=row.get("Investment_Type"),
                    fund_name=row.get("Fund_Name"),
                    annual_return_rate=float(row.get("Annual_Return_Rate") or 0.0),
                    volatility=float(row.get("Volatility") or 0.0),
                    fees_percentage=float(row.get("Fees_Percentage") or 0.0),
                    projected_pension_amount=float(row.get("Projected_Pension_Amount") or 0.0),
                    expected_annual_payout=float(row.get("Expected_Annual_Payout") or 0.0),
                    inflation_adjusted_payout=float(row.get("Inflation_Adjusted_Payout") or 0.0),
                    years_of_payout=int(row.get("Years_of_Payout") or 0),
                    survivor_benefits=row.get("Survivor_Benefits"),
                    transaction_id=row.get("Transaction_ID"),
                    transaction_amount=float(row.get("Transaction_Amount") or 0.0),
                    transaction_date=transaction_date,
                    suspicious_flag=row.get("Suspicious_Flag"),
                    anomaly_score=float(row.get("Anomaly_Score") or 0.0),
                    marital_status=row.get("Marital_Status"),
                    number_of_dependents=int(row.get("Number_of_Dependents") or 0),
                    education_level=row.get("Education_Level"),
                    health_status=row.get("Health_Status"),
                    life_expectancy_estimate=int(row.get("Life_Expectancy_Estimate") or 0),
                    home_ownership_status=row.get("Home_Ownership_Status"),
                    debt_level=float(row.get("Debt_Level") or 0.0),
                    monthly_expenses=float(row.get("Monthly_Expenses") or 0.0),
                    savings_rate=float(row.get("Savings_Rate") or 0.0),
                    investment_experience_level=row.get("Investment_Experience_Level"),
                    financial_goals=row.get("Financial_Goals"),
                    insurance_coverage=row.get("Insurance_Coverage"),
                    portfolio_diversity_score=float(row.get("Portfolio_Diversity_Score") or 0.0),
                    tax_benefits_eligibility=row.get("Tax_Benefits_Eligibility"),
                    government_pension_eligibility=row.get("Government_Pension_Eligibility"),
                    private_pension_eligibility=row.get("Private_Pension_Eligibility"),
                    pension_type=row.get("Pension_Type"),
                    withdrawal_strategy=row.get("Withdrawal_Strategy"),
                    transaction_channel=row.get("Transaction_Channel"),
                    ip_address=row.get("IP_Address"),
                    device_id=row.get("Device_ID"),
                    geo_location=row.get("Geo_Location"),
                    time_of_transaction=time_of_transaction,
                    transaction_pattern_score=float(row.get("Transaction_Pattern_Score") or 0.0),
                    previous_fraud_flag=row.get("Previous_Fraud_Flag"),
                    account_age=int(row.get("Account_Age") or 0)
                )
                db.add(pension)
                pension_records_created += 1
            
            db.commit()
            print(f"✅ Pension data imported: {users_created} users, {pension_records_created} records")
            
        except FileNotFoundError:
            print("⚠️  Excel file not found. Skipping data import.")
            print("   Make sure 'pension_data.xlsx' is in the same directory as this script")
        except Exception as e:
            print(f"❌ Error importing data: {e}")
            db.rollback()

        # Step 3: Create advisor users
        print("\n📋 Step 3: Creating advisor users...")
        advisor_users = [
            {"full_name": "John Smith", "email": "advisor1@example.com", "role": "advisor"},
            {"full_name": "Sarah Johnson", "email": "advisor2@example.com", "role": "advisor"},
            {"full_name": "Michael Brown", "email": "advisor3@example.com", "role": "advisor"}
        ]
        
        created_advisor_ids = []
        for advisor_data in advisor_users:
            existing_user = db.query(User).filter(User.email == advisor_data["email"]).first()
            if not existing_user:
                new_advisor = User(
                    full_name=advisor_data["full_name"],
                    email=advisor_data["email"],
                    password=hash_password("password-123"),
                    role=advisor_data["role"]
                )
                db.add(new_advisor)
                db.commit()
                db.refresh(new_advisor)
                created_advisor_ids.append(new_advisor.id)
                print(f"   ✅ Created advisor: {advisor_data['full_name']}")
            else:
                if existing_user.role == "advisor":
                    created_advisor_ids.append(existing_user.id)
                print(f"   ⚠️  Advisor {advisor_data['email']} already exists")

        # Step 4: Create regulator users
        print("\n📋 Step 4: Creating regulator users...")
        regulator_users = [
            {"full_name": "Regulatory Officer 1", "email": "regulator1@example.com", "role": "regulator"},
            {"full_name": "Regulatory Officer 2", "email": "regulator2@example.com", "role": "regulator"}
        ]
        
        for regulator_data in regulator_users:
            existing_user = db.query(User).filter(User.email == regulator_data["email"]).first()
            if not existing_user:
                new_regulator = User(
                    full_name=regulator_data["full_name"],
                    email=regulator_data["email"],
                    password=hash_password("password-123"),
                    role=regulator_data["role"]
                )
                db.add(new_regulator)
                db.commit()
                db.refresh(new_regulator)
                print(f"   ✅ Created regulator: {regulator_data['full_name']}")
            else:
                print(f"   ⚠️  Regulator {regulator_data['email']} already exists")

        # Step 5: Assign residents to advisors
        if created_advisor_ids:
            print("\n📋 Step 5: Assigning residents to advisors...")
            primary_advisor_id = created_advisor_ids[0]
            
            # Get existing residents
            residents = db.query(User).filter(User.role == "resident").all()
            
            for resident in residents[:5]:  # Assign first 5 residents
                existing_assignment = db.query(AdvisorClient).filter(
                    AdvisorClient.advisor_id == primary_advisor_id,
                    AdvisorClient.resident_id == resident.id
                ).first()
                
                if not existing_assignment:
                    new_assignment = AdvisorClient(
                        advisor_id=primary_advisor_id,
                        resident_id=resident.id
                    )
                    db.add(new_assignment)
                    print(f"   ✅ Assigned resident {resident.full_name} to advisor")
            
            db.commit()

        # Final summary
        print("\n🎉 Railway database setup completed!")
        print("\n📊 SUMMARY:")
        print("=" * 50)
        
        total_users = db.query(User).count()
        advisor_count = db.query(User).filter(User.role == "advisor").count()
        regulator_count = db.query(User).filter(User.role == "regulator").count()
        resident_count = db.query(User).filter(User.role == "resident").count()
        pension_count = db.query(PensionData).count()
        assignment_count = db.query(AdvisorClient).count()
        
        print(f"👥 Total Users: {total_users}")
        print(f"   👨‍💼 Advisors: {advisor_count}")
        print(f"   🏛️  Regulators: {regulator_count}")
        print(f"   🏠 Residents: {resident_count}")
        print(f"📊 Pension Records: {pension_count}")
        print(f"🔗 Advisor-Client Assignments: {assignment_count}")
        
        print("\n🔑 Login Credentials:")
        print("=" * 50)
        print("All users have password: password-123")
        print("\nAdvisors:")
        for advisor_data in advisor_users:
            print(f"   📧 {advisor_data['email']} → {advisor_data['full_name']}")
        
        print("\nRegulators:")
        for regulator_data in regulator_users:
            print(f"   📧 {regulator_data['email']} → {regulator_data['full_name']}")
        
        print("\nResidents:")
        residents = db.query(User).filter(User.role == "resident").limit(5).all()
        for resident in residents:
            print(f"   📧 {resident.email} → {resident.full_name}")
        
        if len(residents) > 5:
            print(f"   ... and {len(residents) - 5} more residents")
        
    except Exception as e:
        print(f"❌ Fatal error during setup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Railway Complete Database Setup Script (MySQL Version)")
    print("=" * 50)
    print("Make sure you have:")
    print("1. DATABASE_URL environment variable set")
    print("2. pension_data.xlsx file in the same directory")
    print("3. All required Python packages installed")
    print("=" * 50)
    
    setup_railway_database()
    
    print("\n✨ Script completed!")
    print("\nNext steps:")
    print("1. Verify your database on Railway")
    print("2. Test login with the created users")
    print("3. Check that all data was imported correctly")

