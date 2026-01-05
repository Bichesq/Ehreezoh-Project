import requests
import json

def inspect_rooms():
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1/ws/debug/rooms")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_rooms()
