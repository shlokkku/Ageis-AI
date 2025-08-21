# In the server directory, create update_password.py
from app.database import SessionLocal
from app import models, security

def update_test_password():
    db = SessionLocal()
    try:
        # Hash the new password
        hashed_password = security.hash_password("password-123")
        
        # Update all users (or specific ones)
        users = db.query(models.User).filter(models.User.id <= 10).all()
        
        for user in users:
            user.password = hashed_password
            print(f"Updated password for user: {user.email}")
        
        db.commit()
        print(f"✅ Updated {len(users)} users with password: password-123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_test_password()