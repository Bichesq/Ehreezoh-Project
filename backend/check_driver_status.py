from app.core.database import SessionLocal
from app.models.driver import Driver
from app.models.user import User

def check_driver():
    db = SessionLocal()
    user_id = "416e997b-ff67-4cc7-9a26-ef054d651bcb"
    
    print(f"Checking status for User: {user_id}")
    
    driver = db.query(Driver).filter(Driver.user_id == user_id).first()
    
    if not driver:
        print("❌ Driver profile not found!")
    else:
        print(f"✅ Driver Found: {driver.id}")
        print(f"   - Is Online: {driver.is_online}")
        print(f"   - Is Available: {driver.is_available}")
        print(f"   - Is Verified: {driver.is_verified}")
        print(f"   - Vehicle Type: {driver.vehicle_type}")
        print(f"   - Current Lat/Lng: {driver.current_latitude}, {driver.current_longitude}")

    db.close()

if __name__ == "__main__":
    check_driver()
