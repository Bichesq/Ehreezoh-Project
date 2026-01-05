import sys
import os
import requests
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))
from app.core.database import SessionLocal
from app.models.ride import Ride

def trigger_debug():
    db = SessionLocal()
    try:
        # Find the LATEST COMPLETED Ride
        print("🔍 Checking for 'completed' ride...")
        ride = db.query(Ride).filter(
            Ride.status == 'completed'
        ).order_by(Ride.updated_at.desc()).first()

        if not ride:
            print("❌ No 'completed' ride found.")
            return

        print(f"🎯 Target Ride ID: {ride.id}")
        
        # Call debug endpoint
        url = f"http://127.0.0.1:8000/api/v1/rides/{ride.id}/debug_broadcast_completion"
        print(f"🚀 Calling {url}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ Broadcast Triggered!")
        else:
            print(f"❌ Failed: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    trigger_debug()
