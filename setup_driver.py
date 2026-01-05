
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.driver import Driver

def make_user_driver(user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User {user_id} not found")
            return

        print(f"Found user: {user.phone_number}")
        
        # Check if driver exists
        driver = db.query(Driver).filter(Driver.user_id == user.id).first()
        if not driver:
            print("Creating driver profile...")
            driver = Driver(
                user_id=user.id,
                vehicle_type="moto",
                vehicle_plate_number="TEST-001",
                is_verified=True,
                is_online=True,
                is_available=True
            )
            db.add(driver)
            user.is_driver = True  # Update user flag
        else:
            print("Driver profile exists. Updating status...")
            driver.is_verified = True
            driver.is_online = True
            driver.is_available = True
            user.is_driver = True

        db.commit()
        print("✅ User is now a verified online driver")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # User ID from the logs
    target_user_id = "416e997b-ff67-4cc7-9a26-ef054d651bcb"
    make_user_driver(target_user_id)
