from app.core.database import SessionLocal
from app.services.matching_service import matching_service
from app.models.user import User

def debug_matching():
    db = SessionLocal()
    
    # Coordinates used in verify_dispatch.js
    pickup_lat = 4.0500
    pickup_lng = 9.7000
    
    print(f"🔎 DEBUG: Searching for drivers at {pickup_lat}, {pickup_lng}")
    
    # Manually seed Redis
    from app.services.redis_service import redis_service
    driver_id_match = "416e997b-ff67-4cc7-9a26-ef054d651bcb"
    
    print(f"   -> Seeding Redis for driver {driver_id_match}...")
    redis_service.update_driver_location(driver_id_match, pickup_lat, pickup_lng, ttl_seconds=600)
    
    drivers = matching_service.find_available_drivers(
        db=db,
        pickup_latitude=pickup_lat,
        pickup_longitude=pickup_lng,
        ride_type="moto",
        radius_km=10.0
    )
    
    print(f"✅ Found {len(drivers)} drivers")
    for d in drivers:
        print(f"   - Driver: {d['full_name']} (ID: {d['driver_id']})")
        print(f"     Dist: {d['distance_km']} km")
        print(f"     Rating: {d['average_rating']}")

    db.close()

if __name__ == "__main__":
    debug_matching()
