import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.driver import Driver

def promote_driver(phone_number):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            print(f"❌ User {phone_number} not found")
            return

        print(f"Found user: {user.id}")
        
        driver = db.query(Driver).filter(Driver.user_id == user.id).first()
        if not driver:
            print("creating new driver profile...")
            driver = Driver(
                user_id=user.id,
                vehicle_type="moto",
                vehicle_make="Test",
                vehicle_model="Moto",
                vehicle_plate_number="TEST-DRIVER",
                vehicle_color="Black",
                driver_license_number="DL-TEST",
                is_verified=True,
                verification_status="approved",
                is_online=False, # Will be set by WS
                is_available=True,
                current_latitude=4.05,
                current_longitude=9.70
            )
            db.add(driver)
        else:
            print("updating existing driver profile...")
            driver.vehicle_type = "moto"
            driver.is_verified = True
            driver.verification_status = "approved"
            driver.is_available = True
        
        user.is_driver = True
        db.commit()
        print(f"✅ User {phone_number} promoted to Driver!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        promote_driver(sys.argv[1])
    else:
        print("Usage: python promote_driver.py <phone_number>")
