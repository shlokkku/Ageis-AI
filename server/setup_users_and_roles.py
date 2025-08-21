#!/usr/bin/env python3
"""
Script to set up advisor and regulator users and assign residents to advisors.
This script will:
1. Create advisor users with role 'advisor'
2. Create regulator users with role 'regulator' 
3. Set all passwords to 'password-123'
4. Assign residents (users 1-5) to advisor user 1
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path so we can import from app
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(app_dir))

try:
    from app.database import SessionLocal
    from app.models import User, AdvisorClient
    from app.security import hash_password
    from sqlalchemy.exc import IntegrityError
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

def create_users_and_assignments():
    """Create advisor and regulator users and assign residents to advisors."""
    
    db = SessionLocal()
    try:
        print("🔧 Setting up users and role assignments...")
        
        # Create advisor users
        advisor_users = [
            {
                "full_name": "John Smith",
                "email": "advisor1@example.com",
                "role": "advisor",
                "password": "password-123"
            },
            {
                "full_name": "Sarah Johnson", 
                "email": "advisor2@example.com",
                "role": "advisor",
                "password": "password-123"
            },
            {
                "full_name": "Michael Brown",
                "email": "advisor3@example.com", 
                "role": "advisor",
                "password": "password-123"
            }
        ]
        
        # Create regulator users
        regulator_users = [
            {
                "full_name": "Regulatory Officer 1",
                "email": "regulator1@example.com",
                "role": "regulator", 
                "password": "password-123"
            },
            {
                "full_name": "Regulatory Officer 2",
                "email": "regulator2@example.com",
                "role": "regulator",
                "password": "password-123"
            }
        ]
        
        created_advisor_ids = []
        
        # Create advisor users
        print("\n📋 Creating advisor users...")
        for advisor_data in advisor_users:
            try:
                # Check if user already exists
                existing_user = db.query(User).filter(User.email == advisor_data["email"]).first()
                if existing_user:
                    print(f"   ⚠️  Advisor {advisor_data['email']} already exists (ID: {existing_user.id})")
                    if existing_user.role == "advisor":
                        created_advisor_ids.append(existing_user.id)
                    continue
                
                # Create new advisor user
                hashed_password = hash_password(advisor_data["password"])
                new_advisor = User(
                    full_name=advisor_data["full_name"],
                    email=advisor_data["email"],
                    password=hashed_password,
                    role=advisor_data["role"]
                )
                
                db.add(new_advisor)
                db.commit()
                db.refresh(new_advisor)
                
                created_advisor_ids.append(new_advisor.id)
                print(f"   ✅ Created advisor: {advisor_data['full_name']} (ID: {new_advisor.id})")
                
            except IntegrityError as e:
                db.rollback()
                print(f"   ❌ Error creating advisor {advisor_data['email']}: {e}")
            except Exception as e:
                db.rollback()
                print(f"   ❌ Unexpected error creating advisor {advisor_data['email']}: {e}")
        
        # Create regulator users
        print("\n📋 Creating regulator users...")
        for regulator_data in regulator_users:
            try:
                # Check if user already exists
                existing_user = db.query(User).filter(User.email == regulator_data["email"]).first()
                if existing_user:
                    print(f"   ⚠️  Regulator {regulator_data['email']} already exists (ID: {existing_user.id})")
                    continue
                
                # Create new regulator user
                hashed_password = hash_password(regulator_data["password"])
                new_regulator = User(
                    full_name=regulator_data["full_name"],
                    email=regulator_data["email"],
                    password=hashed_password,
                    role=regulator_data["role"]
                )
                
                db.add(new_regulator)
                db.commit()
                db.refresh(new_regulator)
                
                print(f"   ✅ Created regulator: {regulator_data['full_name']} (ID: {new_regulator.id})")
                
            except IntegrityError as e:
                db.rollback()
                print(f"   ❌ Error creating regulator {regulator_data['email']}: {e}")
            except Exception as e:
                db.rollback()
                print(f"   ❌ Unexpected error creating regulator {regulator_data['email']}: {e}")
        
        # Assign residents to advisor (user ID 1)
        if created_advisor_ids:
            primary_advisor_id = created_advisor_ids[0]  # Use first advisor created
            print(f"\n📋 Assigning residents to advisor (ID: {primary_advisor_id})...")
            
            # Get existing residents (users 1-5)
            resident_ids = list(range(1, 6))  # [1, 2, 3, 4, 5]
            
            for resident_id in resident_ids:
                try:
                    # Check if assignment already exists
                    existing_assignment = db.query(AdvisorClient).filter(
                        AdvisorClient.advisor_id == primary_advisor_id,
                        AdvisorClient.resident_id == resident_id
                    ).first()
                    
                    if existing_assignment:
                        print(f"   ⚠️  Resident {resident_id} already assigned to advisor {primary_advisor_id}")
                        continue
                    
                    # Create new assignment
                    new_assignment = AdvisorClient(
                        advisor_id=primary_advisor_id,
                        resident_id=resident_id
                    )
                    
                    db.add(new_assignment)
                    db.commit()
                    
                    print(f"   ✅ Assigned resident {resident_id} to advisor {primary_advisor_id}")
                    
                except IntegrityError as e:
                    db.rollback()
                    print(f"   ❌ Error assigning resident {resident_id}: {e}")
                except Exception as e:
                    db.rollback()
                    print(f"   ❌ Unexpected error assigning resident {resident_id}: {e}")
        
        print("\n🎉 User setup completed!")
        
        # Display summary
        print("\n📊 SUMMARY:")
        print("=" * 50)
        
        # Count users by role
        advisor_count = db.query(User).filter(User.role == "advisor").count()
        regulator_count = db.query(User).filter(User.role == "regulator").count()
        resident_count = db.query(User).filter(User.role == "resident").count()
        
        print(f"👥 Total Users: {advisor_count + regulator_count + resident_count}")
        print(f"   👨‍💼 Advisors: {advisor_count}")
        print(f"   🏛️  Regulators: {regulator_count}")
        print(f"   🏠 Residents: {resident_count}")
        
        # Count advisor-client assignments
        assignment_count = db.query(AdvisorClient).count()
        print(f"🔗 Advisor-Client Assignments: {assignment_count}")
        
        print("\n🔑 Login Credentials:")
        print("=" * 50)
        print("All new users have password: password-123")
        print("\nAdvisors:")
        for advisor_data in advisor_users:
            print(f"   📧 {advisor_data['email']} → {advisor_data['full_name']}")
        
        print("\nRegulators:")
        for regulator_data in regulator_users:
            print(f"   📧 {regulator_data['email']} → {regulator_data['full_name']}")
        
        print("\nResidents (existing):")
        residents = db.query(User).filter(User.role == "resident").all()
        for resident in residents:
            print(f"   📧 {resident.email} → {resident.full_name} (ID: {resident.id})")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting user setup script...")
    create_users_and_assignments()
    print("\n✨ Script completed!")
