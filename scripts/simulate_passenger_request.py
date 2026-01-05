import sys
import os
import requests
import time
import json
import redis


# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from app.core.config import settings
from app.models.driver import Driver
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

API_URL = "http://127.0.0.1:8000/api/v1"
PASSENGER_PHONE = "+237000000001" # Distinct mock passenger

def simulate_passenger_request():
    print("🤖 Simulating Passenger Request...")
    
    # 1. Login/Register "Test Passenger"
    auth_payload = {
        "firebase_token": f"mock_token_{PASSENGER_PHONE}",
        "full_name": "Test Passenger",
        "email": "passenger@test.com"
    }
    
    try:
        # Register first (idempotent usually, or fail if exists)
        requests.post(f"{API_URL}/auth/register", json=auth_payload)
    except:
        pass
        
    # Login to get token
    print("🔑 Logging in as Test Passenger...")
    resp = requests.post(f"{API_URL}/auth/login", json={"firebase_token": f"mock_token_{PASSENGER_PHONE}"})
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        return
        
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create valid session
    db = SessionLocal()
    
    # Debug: Check active WS connections
    try:
        ws_debug = requests.get(f"{API_URL}/ws/debug/rooms").json()
        active_users = ws_debug.get("active_users", [])
        print(f"🔌 Active WS Users: {active_users}")
    except Exception as e:
        print(f"⚠️ Could not check WS stats: {e}")
        active_users = []

    # Get all online drivers
    drivers = db.query(Driver).filter(Driver.is_online == True).all()
    
    target_driver = None
    
    # Priority: Online in DB AND Connected to WS
    for d in drivers:
        if str(d.user_id) in active_users:
            target_driver = d
            break
            
    # Fallback: Any online driver (if none connected to WS, likely failure but continue)
    if not target_driver and drivers:
        target_driver = drivers[0]
        print("⚠️ Warning: Driver found in DB but NOT connected to WebSocket. Notification might fail.")
    
    
    if not target_driver:
        print("❌ No Online Driver found! Ensure your app is open and 'Online'.")
        # Default fallback (Banur, Punjab)
        pickup_lat, pickup_lng = 30.555, 76.717 
    else:
        print(f"📍 Found Driver: {target_driver.vehicle_plate_number} (User ID: {target_driver.user_id})")
        
        # Check connection status
        is_connected = str(target_driver.user_id) in active_users
        if is_connected:
             print("✅ Driver is verified CONNECTED to WebSocket")
        else:
             print("❌ Driver is NOT in active connection list!")

        # Get Location (Try DB first, then Redis)
        if target_driver.current_latitude and target_driver.current_longitude:
             pickup_lat, pickup_lng = float(target_driver.current_latitude), float(target_driver.current_longitude)
             print(f"   Location (from DB): {pickup_lat}, {pickup_lng}")
        else:
             # Try Redis
             try:
                 rides_redis = redis.from_url("redis://localhost:6379/0", decode_responses=True)
                 loc_json = rides_redis.get(f"driver:{target_driver.id}:location")
                 if not loc_json:
                      # If ID mismatch, try using user_id or just check geo index? 
                      # redis_service uses driver_id
                      pass
                      
                 if loc_json:
                      loc_data = json.loads(loc_json)
                      pickup_lat = float(loc_data['latitude'])
                      pickup_lng = float(loc_data['longitude'])
                      print(f"   Location (from Redis): {pickup_lat}, {pickup_lng}")
                 else:
                      print("⚠️ Location not found in DB or Redis. Using default (Banur, Punjab).")
                      pickup_lat, pickup_lng = 30.555, 76.717 # Banur, Punjab
             except Exception as e:
                 print(f"⚠️ Failed to check Redis: {e}")
                 pickup_lat, pickup_lng = 30.555, 76.717 # Banur, Punjab
    
    db.close()

    # 3. Setup Pickup (At Driver's Location)
    ride_request = {
        "ride_type": "moto",
        "pickup_latitude": pickup_lat,
        "pickup_longitude": pickup_lng,
        "pickup_address": "Driver Location (Simulation)",
        "dropoff_latitude": pickup_lat + 0.01,
        "dropoff_longitude": pickup_lng + 0.01,
        "dropoff_address": "Nearby Dropoff"
    }
    
    # 4. Request Ride
    print(f"🚀 Requesting Ride near driver...")
    resp = requests.post(f"{API_URL}/rides/request", json=ride_request, headers=headers)
    
    if resp.status_code in [200, 201]:
        ride_data = resp.json()
        print(f"✅ Request Sent! Ride ID: {ride_data['id']}")
        print("⌛ Check your Mobile App for the popup!")
    else:
        print(f"❌ Request Failed: {resp.text}")

if __name__ == "__main__":
    simulate_passenger_request()
