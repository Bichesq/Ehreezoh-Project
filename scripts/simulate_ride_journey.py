import sys
import os
import json
import redis
import requests
import time
from sqlalchemy.orm import Session

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.driver import Driver
from app.models.ride import Ride
from app.core.auth import create_access_token

def simulate_ride_journey():
    db = SessionLocal()
    try:
        # 2. Find the LATEST ACTIVE (Accepted) Ride globally
        # This is more robust for testing than finding a driver first
        print("🔍 Checking for any accepted ride...")
        ride = db.query(Ride).filter(
            Ride.status == 'accepted'
        ).order_by(Ride.updated_at.desc()).first()

        if not ride:
            print("❌ No 'accepted' ride found in the system.")
            return

        print(f"🎯 Target Ride ID: {ride.id}")
        
        driver = ride.driver
        if not driver:
             print("❌ Ride has no driver assigned (Data integrity error)")
             return

        print(f"🚕 Driver found: {driver.id} (User: {driver.user_id})")
        
        # 3. Forge Auth Token
        access_token = create_access_token(
            data={"sub": str(driver.user_id), "phone": driver.user.phone_number}
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 4. Start Ride
        print("\n🚀 Starting Ride...")
        start_url = f"http://127.0.0.1:8000/api/v1/rides/{ride.id}/start"
        start_response = requests.patch(start_url, headers=headers)
        
        if start_response.status_code == 200:
            print("✅ Ride STARTED! (Check Mobile UI - Should say 'Heading to destination' or similar)")
        else:
            print(f"❌ Failed to start ride: {start_response.text}")
            return

        # 5. Simulate Drive Time
        print("\n⏳ Driving... (Waiting 10 seconds)")
        time.sleep(10)

        # 6. Complete Ride
        print("\n🏁 Completing Ride...")
        complete_url = f"http://127.0.0.1:8000/api/v1/rides/{ride.id}/complete"
        # Optional: Add final fare query param
        complete_response = requests.patch(complete_url, headers=headers)

        if complete_response.status_code == 200:
             print("✅ Ride COMPLETED! (Check Mobile UI - Should show Payment/Rating)")
             print("Response:", complete_response.json())
        else:
             print(f"❌ Failed to complete ride: {complete_response.text}")

    except Exception as e:
        print(f"❌ Error simulating journey: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    simulate_ride_journey()
