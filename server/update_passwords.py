#!/usr/bin/env python3
"""
Password Update Script
Updates all existing user passwords from bcrypt to sha256_crypt hashing
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.security import hash_password

def update_passwords():
    """Update all user passwords to use new hashing method"""
    
    # Get DATABASE_URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable not found!")
        return
    
    print("🔐 Starting password update process...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        print(f"📊 Found {len(users)} users to update")
        
        updated_count = 0
        for user in users:
            try:
                # Update password to new hash
                new_password_hash = hash_password("password-123")
                user.password = new_password_hash
                updated_count += 1
                print(f"   ✅ Updated password for: {user.email}")
            except Exception as e:
                print(f"   ❌ Failed to update {user.email}: {e}")
        
        # Commit changes
        db.commit()
        print(f"\n🎉 Successfully updated {updated_count} user passwords!")
        print("🔑 All users now have password: password-123")
        
    except Exception as e:
        print(f"❌ Error during password update: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_passwords()
