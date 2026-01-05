import sys
import os
import json
import requests
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))
from app.core.database import SessionLocal
from app.models.ride import Ride
from app.core.auth import create_access_token

def simulate_completion():
    db = SessionLocal()
    try:
        # 1. Find the LATEST STARTED Ride
        print("🔍 Checking for 'started' ride...")
        ride = db.query(Ride).filter(
            Ride.status == 'started'
        ).order_by(Ride.updated_at.desc()).first()

        if not ride:
            print("❌ No 'started' ride found. It might have been completed or never started.")
            return

        print(f"🎯 Target Ride ID: {ride.id}")
        
        driver = ride.driver
        if not driver:
             print("❌ Ride has no driver assigned.")
             return

        print(f"🚕 Driver found: {driver.id}")
        
        # 2. Forge Auth Token
        access_token = create_access_token(
            data={"sub": str(driver.user_id), "phone": driver.user.phone_number}
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # 3. Complete Ride
        print("\n🏁 Completing Ride (Retry)...")
        complete_url = f"http://127.0.0.1:8000/api/v1/rides/{ride.id}/complete"
        complete_response = requests.patch(complete_url, headers=headers)

        if complete_response.status_code == 200:
             print("✅ Ride COMPLETED! (Check Mobile UI for Payment/Rating)")
             print("Response:", complete_response.json())
        else:
             print(f"❌ Failed to complete ride: {complete_response.text}")

    except Exception as e:
        print(f"❌ Error simulating completion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    simulate_completion()
