#!/usr/bin/env python3
"""
Test script to verify authentication logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app import security
from app.database import get_db
from app import models

def test_password_hashing():
    """Test password hashing and verification"""
    print("=== Testing Password Hashing Logic ===")
    
    # Test password
    test_password = 'password123'
    
    # Hash the password
    hashed_password = security.hash_password(test_password)
    print(f"🔐 Original password: {test_password}")
    print(f"🔐 Hashed password: {hashed_password}")
    
    # Verify the password
    is_valid = security.verify_password(test_password, hashed_password)
    print(f"✅ Password verification: {is_valid}")
    
    # Test with wrong password
    wrong_password = 'wrongpassword'
    is_wrong = security.verify_password(wrong_password, hashed_password)
    print(f"❌ Wrong password verification: {is_wrong}")
    
    print("\n🎯 Hashing logic test completed!")

def test_user_creation():
    """Test user creation and password storage"""
    print("\n=== Testing User Creation ===")
    
    try:
        db = next(get_db())
        
        # Create a test user
        test_user = models.User(
            full_name='Test User',
            email='test@example.com',
            password=security.hash_password('password123'),
            role='resident'
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Test user created:")
        print(f"   ID: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print(f"   Password hash: {test_user.password[:30]}...")
        
        # Test password verification
        is_valid = security.verify_password('password123', test_user.password)
        print(f"✅ Stored password verification: {is_valid}")
        
        # Clean up - delete test user
        db.delete(test_user)
        db.commit()
        print("🧹 Test user cleaned up")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error testing user creation: {e}")

if __name__ == "__main__":
    test_password_hashing()
    test_user_creation()
