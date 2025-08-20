#!/usr/bin/env python3
"""
Test script to verify signup and login flow
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app import models
from app import security

def test_signup_login_flow():
    """Test complete signup and login flow"""
    print("=== Testing Signup and Login Flow ===")
    
    try:
        db = next(get_db())
        
        # Test data
        test_email = 'testflow@example.com'
        test_password = 'password123'
        test_name = 'Test Flow User'
        test_role = 'resident'
        
        # Step 1: Check if user exists
        existing_user = db.query(models.User).filter(models.User.email == test_email).first()
        if existing_user:
            print(f"⚠️  User {test_email} already exists, deleting...")
            db.delete(existing_user)
            db.commit()
        
        # Step 2: Create user (simulate signup)
        print(f"\n📝 Creating user: {test_email}")
        hashed_password = security.hash_password(test_password)
        new_user = models.User(
            full_name=test_name,
            email=test_email,
            password=hashed_password,
            role=test_role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ User created successfully:")
        print(f"   ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Role: {new_user.role}")
        print(f"   Password hash: {new_user.password[:30]}...")
        
        # Step 3: Test login (simulate login)
        print(f"\n🔐 Testing login for: {test_email}")
        user = db.query(models.User).filter(models.User.email == test_email).first()
        
        if not user:
            print("❌ User not found during login")
            return
        
        # Verify password
        if security.verify_password(test_password, user.password):
            print("✅ Login successful - password verified")
            
            # Create JWT token
            access_token = security.create_access_token(
                data={"user_id": user.id, "role": user.role}
            )
            print(f"🎫 JWT token created: {access_token[:50]}...")
            
        else:
            print("❌ Login failed - password verification failed")
        
        # Clean up
        print(f"\n🧹 Cleaning up test user...")
        db.delete(new_user)
        db.commit()
        print("✅ Test user cleaned up")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error in signup/login flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signup_login_flow()
