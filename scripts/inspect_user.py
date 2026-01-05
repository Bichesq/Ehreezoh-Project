
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from app.core.config import settings
from app.models.driver import Driver
from app.models.user import User

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user(user_id):
    db = SessionLocal()
    print(f"🔍 Inspecting User ID: {user_id}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print("❌ User NOT found in DB")
        return

    print(f"👤 Name: {user.full_name}, Phone: {user.phone_number}")
    print(f"   Is Driver: {user.is_driver}")
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    if driver:
        print(f"🚕 Driver Profile Found. Status: Online={driver.is_online}, Verified={driver.is_verified}")
        print(f"   Location: {driver.current_latitude}, {driver.current_longitude}")
    else:
        print("❌ No Driver profile found for this user")

    db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_user(sys.argv[1])
    else:
        print("Please provide a user ID")
