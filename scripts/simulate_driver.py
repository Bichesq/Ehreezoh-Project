import asyncio
import json
import logging
import sys
import os
import requests
import websockets

# Add backend directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from app.core.config import settings
from app.models.driver import Driver
from app.models.user import User
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database Setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"
WS_URL = "ws://127.0.0.1:8000/api/v1/ws/connect"

# Driver Credentials
DRIVER_PHONE = "+237699000005" 

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def simulate_driver():
    # 1. Login/Register
    logger.info(f"🔑 Logging in as Driver {DRIVER_PHONE}...")
    
    # Try Register
    try:
        requests.post(f"{API_URL}/auth/register", json={
            "firebase_token": f"mock_token_{DRIVER_PHONE}",
            "full_name": "Simulated Driver 5",
            "is_driver": True
        })
    except:
        pass # Ignore if exists

    # Login
    try:
        response = requests.post(f"{API_URL}/auth/login", json={
            "firebase_token": f"mock_token_{DRIVER_PHONE}"
        })
        response.raise_for_status()
        tokens = response.json()
        access_token = tokens["access_token"]
        user_id = tokens["user"]["id"]
        logger.info(f"✅ Logged in! User ID: {user_id}")
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        try:
            logger.error(f"Response: {response.text}")
        except:
            pass
        return

    # 2. Ensure Driver Profile & Verification
    try:
        # Check if driver profile exists
        driver_resp = requests.get(f"{API_URL}/drivers/me", headers={"Authorization": f"Bearer {access_token}"})
        if driver_resp.status_code == 404 or driver_resp.status_code == 403:
            logger.info(f"Driver Profile Missing (Status {driver_resp.status_code}). Creating...")
            create_resp = requests.post(
                f"{API_URL}/drivers/register",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "driver_license_number": f"DL-{DRIVER_PHONE[-6:]}",
                    "vehicle_type": "moto",
                    "vehicle_plate_number": f"VP-{DRIVER_PHONE[-4:]}",
                    "vehicle_model": "Honda",
                    "vehicle_color": "Red"
                }
            )
            create_resp.raise_for_status()
            logger.info("✅ Driver Profile Created")
    except Exception as e:
         logger.error(f"❌ Driver profile check/create failed: {e}")
         try:
             # If create failed, log response
             if 'create_resp' in locals():
                 logger.error(f"Create Response: {create_resp.text}")
         except:
             pass
         return

    # Force Verify in DB
    try:
        db = SessionLocal()
        driver = db.query(Driver).filter(Driver.user_id == user_id).first()
        if driver:
            driver.is_verified = True
            driver.is_online = True # Set initial status
            driver.is_available = True
            db.commit()
            logger.info(f"✅ Driver {driver.id} Force Verified & Online in DB")
        db.close()
    except Exception as e:
        logger.error(f"❌ DB Update failed: {e}")

    # 3. Connect to WebSocket
    ws_url_with_token = f"{WS_URL}?token={access_token}"
    logger.info(f"🔌 Connecting to WebSocket at {ws_url_with_token}...")
    
    async with websockets.connect(ws_url_with_token) as websocket:
        logger.info("✅ WebSocket Connected! Waiting for offers...")
        
        async def broadcast_location():
            # User Coords (Pickup)
            pickup_lat = 30.562034
            pickup_lon = 76.716748
            
            # Start slightly away (South West)
            current_lat = 30.558000
            current_lon = 76.713000
            
            # Dropoff (North East)
            dropoff_lat = 30.565000
            dropoff_lon = 76.720000
            
            nonlocal vehicle_reached_pickup, ride_started
            
            target_lat = pickup_lat
            target_lon = pickup_lon
            mode = "PICKUP"
            
            logger.info(f"📡 Starting location broadcast. Mode: {mode}")
            
            while True:
                try:
                    # Check if mode changed to DROPOFF
                    if ride_started and mode == "PICKUP":
                        mode = "DROPOFF"
                        target_lat = dropoff_lat
                        target_lon = dropoff_lon
                        logger.info("🔄 Switched navigation target to DROPOFF")

                    # Calculate Step (re-calc every loop for dynamic targets)
                    lat_diff = target_lat - current_lat
                    lon_diff = target_lon - current_lon
                    dist = (lat_diff**2 + lon_diff**2)**0.5
                    
                    if dist > 0.0001:
                        # Move towards target
                        step_size = 0.0002 # Speed
                        current_lat += (lat_diff / dist) * step_size
                        current_lon += (lon_diff / dist) * step_size
                    else:
                        if mode == "PICKUP" and not vehicle_reached_pickup:
                            vehicle_reached_pickup = True
                            logger.info("🚖 Arrived at Pickup Location!")
                        elif mode == "DROPOFF":
                            logger.info("🚖 Arrived at Dropoff Location!")

                    await websocket.send(json.dumps({
                        "type": "driver_location_update",
                        "data": {"latitude": current_lat, "longitude": current_lon}
                    }))
                    logger.info(f"📍 Location update: {current_lat:.6f}, {current_lon:.6f} ({mode})")
                    await asyncio.sleep(2) # Update every 2s
                except Exception as e:
                    logger.error(f"Broadcast error: {e}")
                    break
        
        # Initialize flags in outer scope
        vehicle_reached_pickup = False 
        ride_started = False
        
        asyncio.create_task(broadcast_location())

        # 3. Go Online (Send location via API to ensure DB+Redis update)
        lat = 30.558000
        lon = 76.713000
        try:
            loc_resp = requests.post(
                f"{API_URL}/drivers/location",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"latitude": lat, "longitude": lon}
            )
            if loc_resp.status_code == 200:
                logger.info(f"✅ Location synced via API: {lat}, {lon}")
            else:
                logger.error(f"❌ Location sync failed: {loc_resp.text}")
        except Exception as e:
            logger.error(f"❌ Location API error: {e}")

        # Send via WS as well
        await websocket.send(json.dumps({
            "type": "driver_location_update",
            "data": {"latitude": lat, "longitude": lon}
        }))
        logger.info("📍 Sent initial location (Online)")
        
        # Keep connection alive and listen
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                event_type = data.get("type")
                
                logger.info(f"📩 Received Event: {event_type}")
                
                if event_type == "new_ride_offer":
                    offer = data.get("data")
                    ride_id = offer.get("ride_id")
                    logger.info(f"🔔 NEW RIDE OFFER! ID: {ride_id}")
                    logger.info(f"   Fare: {offer.get('estimated_fare')}")
                    logger.info(f"   Pickup: {offer.get('pickup_address')}")
                    
                    # Accept the ride
                    logger.info("🚀 Accepting Ride in 2 seconds...")
                    await asyncio.sleep(2)
                    
                    try:
                        accept_response = requests.patch(
                            f"{API_URL}/rides/{ride_id}/accept",
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        accept_response.raise_for_status()
                        logger.info("✅ RIDE ACCEPTED! Flow Complete.")
                        
                        # 4. Ride Lifecycle Simulation
                        vehicle_reached_pickup = False
                        ride_started = False
                        
                        async def ride_lifecycle():
                            nonlocal vehicle_reached_pickup, ride_started
                            
                            # A. DRIVE TO PICKUP
                            logger.info("⏳ Waiting to reach pickup...")
                            
                            # Wait until close to pickup (flag set by broadcast loop)
                            timeout = 0
                            while not vehicle_reached_pickup and timeout < 120:
                                await asyncio.sleep(1)
                                timeout += 1
                            
                            if not vehicle_reached_pickup:
                                 logger.warning("⚠️ Timed out waiting for pickup arrival")
                            
                            logger.info("🚖 Driver Arrived at Pickup! (Triggering API)")
                            await asyncio.sleep(2)
                            
                            # B. START RIDE
                            try:
                                logger.info("🚀 Driver Starting Ride...")
                                start_resp = requests.patch(
                                    f"{API_URL}/rides/{ride_id}/start",
                                    headers={"Authorization": f"Bearer {access_token}"}
                                )
                                start_resp.raise_for_status()
                                logger.info("✅ Ride Started! Status Updated.")
                                ride_started = True
                            except Exception as e:
                                logger.error(f"❌ Failed to start ride: {e}")
                                return

                            # C. DRIVE TO DROPOFF
                            # Update target to dropoff
                            logger.info("➡️ Heading to Dropoff...")
                            await asyncio.sleep(8) # Simulate driving time
                            
                            # D. COMPLETE RIDE
                            try:
                                logger.info("🏁 Completing Ride...")
                                complete_resp = requests.patch(
                                    f"{API_URL}/rides/{ride_id}/complete?final_fare={offer.get('estimated_fare')}",
                                    headers={"Authorization": f"Bearer {access_token}"}
                                )
                                complete_resp.raise_for_status()
                                logger.info("✅ Ride Completed! Money made.")
                            except Exception as e:
                                logger.error(f"❌ Failed to complete ride: {e}")

                        # Start lifecycle monitor
                        asyncio.create_task(ride_lifecycle())
                        

                        
                    except Exception as e:
                        logger.error(f"❌ Failed to accept ride: {e}")
                        try:
                             logger.error(f"Response: {accept_response.text}")
                        except:
                             pass
                        
                elif event_type == "ride_cancelled":
                     logger.info("🚫 Ride was cancelled.")

                # Periodically send location updates if "started"?
                # For now, just keep the connection open.
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Connection Closed")
        except Exception as e:
            logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(simulate_driver())
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user")
