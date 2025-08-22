#!/usr/bin/env python3
"""
Quick script to check user roles in the database
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not found!")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("🔍 Checking Database Users...")
    print("=" * 50)
    
    # Check advisors
    print("\n👨‍💼 ADVISORS:")
    advisors = db.execute(text("SELECT id, full_name, email, role FROM users WHERE role = 'advisor'"))
    for row in advisors:
        print(f"   ID: {row.id}, Name: {row.full_name}, Email: {row.email}")
    
    # Check regulators
    print("\n🏛️ REGULATORS:")
    regulators = db.execute(text("SELECT id, full_name, email, role FROM users WHERE role = 'regulator'"))
    for row in regulators:
        print(f"   ID: {row.id}, Name: {row.full_name}, Email: {row.email}")
    
    # Check residents (first 5)
    print("\n🏠 RESIDENTS (First 5):")
    residents = db.execute(text("SELECT id, full_name, email, role FROM users WHERE role = 'resident' LIMIT 5"))
    for row in residents:
        print(f"   ID: {row.id}, Name: {row.full_name}, Email: {row.email}")
    
    # Count totals
    print("\n📊 TOTALS:")
    total_users = db.execute(text("SELECT COUNT(*) as count FROM users")).scalar()
    advisor_count = db.execute(text("SELECT COUNT(*) as count FROM users WHERE role = 'advisor'")).scalar()
    regulator_count = db.execute(text("SELECT COUNT(*) as count FROM users WHERE role = 'regulator'")).scalar()
    resident_count = db.execute(text("SELECT COUNT(*) as count FROM users WHERE role = 'resident'")).scalar()
    
    print(f"   Total Users: {total_users}")
    print(f"   Advisors: {advisor_count}")
    print(f"   Regulators: {regulator_count}")
    print(f"   Residents: {resident_count}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
