import asyncio
import sys
import os
import json
import websockets
import requests
from dotenv import load_dotenv

# Load .env
# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

API_URL = "http://127.0.0.1:8000/api/v1"
WS_URL = "ws://127.0.0.1:8000/api/v1/ws/connect"

from app.core.config import settings
from app.models.user import User
from app.models.driver import Driver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def test_driver_notification():
    # 1. Get valid driver from DB
    db = SessionLocal()
    driver_user = db.query(User).join(Driver).filter(Driver.is_online == True).first()
    db.close()

    if not driver_user:
        print("❌ No Online Driver found in DB!")
        return

    print(f"🔑 Logging in as Driver: {driver_user.phone_number} ({driver_user.full_name})")
    resp = requests.post(f"{API_URL}/auth/login", json={"firebase_token": f"mock_token_{driver_user.phone_number}"}) 
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        return
        
    token = resp.json()['access_token']
    user_id = resp.json()['user']['id']
    print(f"✅ Logged in as Driver {user_id}")

    # 2. Connect to WebSocket
    uri = f"{WS_URL}?token={token}"
    print(f"🔌 Connecting to WS: {uri}")
    
    async with websockets.connect(uri) as websocket:
        print("✅ WebSocket Connected!")
        
        # 3. Wait for messages
        print("👂 Listening for 'new_ride_offer'...")
        
        # Launch simulation script in parallel? 
        # For now, I'll just wait, and manually run the simulation script in another terminal or tool call.
        # OR better: I can trigger the simulation via HTTP request if I had an endpoint, 
        # but I have to run the script.
        
        # We will just listen for 30 seconds.
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(message)
                print(f"📩 Received Message: {data.get('type')}")
                print(json.dumps(data, indent=2))
                
                if data.get('type') == 'new_ride_offer':
                    print("🎉 SUCCESS! Received Ride Offer!")
                    break
        except asyncio.TimeoutError:
            print("❌ Timeout: No message received in 30s")

if __name__ == "__main__":
    asyncio.run(test_driver_notification())
