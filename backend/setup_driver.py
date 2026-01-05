
import sys
import os

# Ensure the script can find 'app' package when run from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
            print("⚠️ Driver profile missing. Creating new one...")
            driver = Driver(
                user_id=user.id,
                vehicle_type="moto",  # Explicitly set to moto
                vehicle_make="Test",
                vehicle_model="Moto",
                vehicle_plate_number="TEST-123",
                vehicle_color="Blue",
                driver_license_number="DL-12345",
                is_verified=True,
                verification_status="approved",
                is_online=True,
                is_available=True,
                current_latitude=4.05,
                current_longitude=9.70
            )
            db.add(driver)
        else:
            print(f"✅ Driver profile exists (ID: {driver.id}). Updating...")
            driver.vehicle_type = "moto"
            driver.is_online = True
            driver.is_available = True
            driver.is_verified = True
        
        user.is_driver = True
        db.commit()
        print("✅ User is now a verified online driver (committed)")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # User ID from the logs
    target_user_id = "416e997b-ff67-4cc7-9a26-ef054d651bcb"
    make_user_driver(target_user_id)
