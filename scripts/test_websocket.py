import asyncio
import websockets
import requests
import json
import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

API_URL = "http://192.168.1.4:8000/api/v1"
WS_URL = "ws://192.168.1.4:8000/api/v1/ws/connect"

async def test_websocket():
    print(f"🔬 Testing WebSocket Connection to {WS_URL}")

    # 1. Login as Driver to get Token
    print("🔑 Logging in as Driver...")
    try:
        resp = requests.post(
            f"{API_URL}/auth/login", 
            json={"firebase_token": "mock_token_+237600000000"} # Assuming this is the test driver phone
        )
        if resp.status_code != 200:
            print(f"⚠️ User not found. Registering...")
            # Try registering if login fails
            reg_resp = requests.post(f"{API_URL}/auth/register", json={
                "firebase_token": "mock_token_+237600000000",
                "full_name": "Test Driver",
                "email": "driver@test.com",
                "is_driver": True
            })
            if reg_resp.status_code not in [200, 201]:
                 print(f"❌ Registration failed: {reg_resp.text}")
                 return
            print("✅ Registered. Logging in...")
            resp = requests.post(f"{API_URL}/auth/login", json={"firebase_token": "mock_token_+237600000000"})
            
        token = resp.json()['access_token']
        print("✅ Got Driver Token")
    except Exception as e:
        print(f"❌ Auth Error: {e}")
        return

    # 2. Connect to WebSocket
    uri = f"{WS_URL}?token={token}"
    print(f"🔌 Connecting to WS...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket Connected Successfully!")
            
            # Wait for welcome message
            msg = await websocket.recv()
            print(f"📩 Received: {msg}")
            
            # Send a ping
            await websocket.send(json.dumps({"type": "ping", "timestamp": "now"}))
            print("📤 Sent Ping")
            
            msg = await websocket.recv()
            print(f"📩 Received Pong: {msg}")
            
            # Keep alive for a few seconds
            await asyncio.sleep(2)
            print("✅ Test Complete. Closing.")
            
    except Exception as e:
        print(f"❌ WebSocket Connection Failed: {e}")

if __name__ == "__main__":
    # Install websockets if needed: pip install websockets
    try:
        asyncio.run(test_websocket())
    except ImportError:
        print("Please install websockets: pip install websockets")
