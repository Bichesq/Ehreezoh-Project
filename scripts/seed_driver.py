import sys
import os
import time
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.driver import Driver
from app.core.auth import hash_phone_number
from app.services.redis_service import redis_service

def seed_driver():
    db = SessionLocal()
    try:
        print("🌱 Seeding test driver...")
        
        # Test Driver Data
        phone = "+237699999999"
        phone_hash = hash_phone_number(phone)
        
        # 1. Create/Get User
        user = db.query(User).filter(User.phone_number == phone).first()
        if not user:
            print(f"Creating user {phone}...")
            user = User(
                phone_number=phone,
                phone_hash=phone_hash,
                firebase_uid="test_firebase_uid_driver",
                full_name="Test Driver",
                email="driver@test.com",
                is_driver=True,
                is_verified=True,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"User {phone} already exists.")

        # 2. Create/Get Driver Profile
        driver = db.query(Driver).filter(Driver.user_id == user.id).first()
        if not driver:
            print("Creating driver profile...")
            driver = Driver(
                user_id=user.id,
                driver_license_number="DL123456789",
                vehicle_type="moto",
                vehicle_plate_number="LT123AB",
                vehicle_color="Yellow",
                is_online=True,
                is_available=True,
                is_verified=True,
                verification_status="approved",
                current_latitude=4.0511,
                current_longitude=9.7679
            )
            db.add(driver)
            db.commit()
            db.refresh(driver)
        else:
            print("Driver profile already exists.")
            # Ensure online
            driver.is_online = True
            driver.is_available = True
            driver.is_verified = True
            db.commit()
            
        print(f"✅ Driver ready: ID={driver.id}, UserID={user.id}")
        
        # 3. Update Redis Location (Crucial for Matching)
        print("📍 Updating Redis location...")
        redis_service.update_driver_location(
            driver_id=user.id, # Note: Matching service uses user_id as driver_id in Redis
            latitude=4.0511,
            longitude=9.7679,
            ttl_seconds=3600 # 1 hour
        )
        redis_service.set_driver_status(
            driver_id=user.id,
            is_online=True,
            is_available=True,
            ttl_seconds=3600
        )
        
        print("✅ Redis updated successfully.")
        
    except Exception as e:
        print(f"❌ Error seeding driver: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_driver()
