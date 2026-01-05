import sys
import os
import json
import redis
import requests
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

def simulate_driver_accept():
    db = SessionLocal()
    try:
        # 1. Get the latest pending request from DB (More reliable than Redis if matching failed)
        print("🔍 checking for latest requested ride in DB...")
        ride = db.query(Ride).filter(Ride.status == 'requested').order_by(Ride.created_at.desc()).first()
        
        if not ride:
            print("❌ No 'requested' rides found in DB.")
            return

        ride_id = ride.id
        print(f"🎯 Target Ride ID: {ride_id} (Created: {ride.created_at})")
        
        # 2. Get the Test Driver
        driver = db.query(Driver).filter(Driver.vehicle_type == "moto", Driver.is_online == True).first()
        if not driver:
            print("❌ No online moto driver found to accept the ride.")
            return
            
        print(f"🚕 Driver found: {driver.id} (User: {driver.user_id})")
        
        # 3. Forge Auth Token
        access_token = create_access_token(
            data={"sub": str(driver.user_id), "phone": driver.user.phone_number}
        )
        print(f"🔑 Forged Access Token for driver.")
        
        # 4. Call API to Accept Ride
        url = f"http://127.0.0.1:8000/api/v1/rides/{ride_id}/accept"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🚀 Sending request to {url}...")
        response = requests.patch(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ API Response: 200 OK")
            print("🎉 Ride ACCEPTED successfully via API.")
            print("Response:", response.json())
        else:
            print(f"❌ API Failed with status {response.status_code}")
            print("Response:", response.text)

    except Exception as e:
        print(f"❌ Error simulating acceptance: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    simulate_driver_accept()
