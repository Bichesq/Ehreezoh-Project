import asyncio
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
load_dotenv(os.path.join(backend_dir, '.env'))

# Add backend directory to path
sys.path.append(backend_dir)

from app.core.config import settings
from app.models.user import User
from app.models.driver import Driver
from app.core.config import settings
from app.models.user import User
from app.models.driver import Driver
# from app.core.security import get_password_hash # Not needed

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def promote_all_recent_users():
    db = SessionLocal()
    try:
        # Get last 10 users
        users = db.query(User).order_by(User.created_at.desc()).limit(10).all()
        if not users:
            print("❌ No users found in database.")
            return

        print(f"🔍 Found {len(users)} recent users. Promoting all to Driver...")
        
        for user in users:
            print(f"Processing: {user.full_name} ({user.phone_number})")
            user.is_driver = True
            
            # Check if Driver profile exists
            driver = db.query(Driver).filter(Driver.user_id == user.id).first()
            if not driver:
                print(f"   ✨ Creating Driver profile for {user.phone_number}")
                driver = Driver(
                    user_id=user.id,
                    vehicle_type='moto',
                    vehicle_plate_number=f'T-{user.phone_number[-4:]}',
                    vehicle_make='Honda',
                    vehicle_model='Dio',
                    vehicle_color='Black',
                    driver_license_number=f"DL-{user.phone_number[-4:]}",
                    is_online=True,
                    is_available=True,
                    is_verified=True,
                    verification_status='approved'
                )
                db.add(driver)
            else:
                print("   ℹ️ Driver profile exists. Verifying...")
                driver.is_online = True
                driver.is_available = True
                driver.is_verified = True
                driver.verification_status = 'approved'
        
        db.commit()
        print(f"✅ Successfully promoted all {len(users)} users to DRIVER!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    promote_all_recent_users()
