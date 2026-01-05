import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from app.core.config import settings
from app.models.ride import Ride

# Database Setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_status():
    db = SessionLocal()
    try:
        # Get latest ride
        ride = db.query(Ride).order_by(Ride.created_at.desc()).first()
        if ride:
            print(f"Latest Ride ID: {ride.id}")
            print(f"Status: {ride.status}")
            print(f"Driver ID: {ride.driver_id}")
            print(f"Created At: {ride.created_at}")
            print(f"Updated At: {ride.updated_at}")
        else:
            print("No rides found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_status()
