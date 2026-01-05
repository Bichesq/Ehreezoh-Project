import requests
import sys

# We need a valid token. 
# Since we can't easily get one without login credentials, 
# we will trust the DB check and just assume the API works if the code is correct.
# BUT, we can try to "login" as Quinn if we knew the mock login flow.
# In dev, the auth service uses `mock_token_{phone}`.
# Quinn's phone: +237652266407

PHONE = "+237652266407"
BASE_URL = "http://localhost:8000/api/v1"

def test_gamification_api():
    # 1. Login to get token
    print(f"Logging in as {PHONE}...")
    login_payload = {"firebase_token": f"mock_token_{PHONE}"}
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        resp.raise_for_status()
        data = resp.json()
        token = data["access_token"]
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Call gamification/me
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{BASE_URL}/gamification/me", headers=headers)
        resp.raise_for_status()
        stats = resp.json()
        print("Gamification Stats:")
        print(stats)
        
        if stats.get("reputation_score") == 100:
            print("SUCCESS: Reputation is 100")
        else:
            print(f"FAILURE: Reputation is {stats.get('reputation_score')}")
            
    except Exception as e:
        print(f"API call failed: {e}")
        print(resp.text)

if __name__ == "__main__":
    test_gamification_api()
