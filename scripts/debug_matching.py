import sys
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from app.core.config import settings
from app.services.matching_service import matching_service
from app.models.driver import Driver
from app.models.user import User

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_matching():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # 1. Print all Online Drivers in DB
        logger.info("--- DB STATE ---")
        drivers = db.query(Driver).filter(Driver.is_online == True).all()
        for d in drivers:
            logger.info(f"Driver {d.id}: Online={d.is_online}, Verified={d.is_verified}, Type={d.vehicle_type}, Loc: {d.current_latitude}, {d.current_longitude}")

        # 2. Test Match at Driver's location
        if not drivers:
            logger.error("NO ONLINE DRIVERS IN DB!")
            return

        target_driver = drivers[0]
        lat = float(target_driver.current_latitude)
        lon = float(target_driver.current_longitude)
        
        logger.info(f"\n--- MATCH TEST 1: Exact Location ({lat}, {lon}) ---")
        matched = matching_service.find_available_drivers(
            db=db,
            pickup_latitude=lat,
            pickup_longitude=lon,
            ride_type=target_driver.vehicle_type,
            radius_km=5.0
        )
        logger.info(f"Found {len(matched)} drivers")
        for m in matched:
            logger.info(f" - {m['full_name']} ({m['distance_km']}km)")

        # 3. Test Match 1km away
        lat_off = lat + 0.009 # approx 1km
        logger.info(f"\n--- MATCH TEST 2: 1km Away ({lat_off}, {lon}) ---")
        matched = matching_service.find_available_drivers(
            db=db,
            pickup_latitude=lat_off,
            pickup_longitude=lon,
            ride_type=target_driver.vehicle_type,
            radius_km=5.0
        )
        logger.info(f"Found {len(matched)} drivers")

        # 4. Test Match Wrong Type
        wrong_type = "car" if target_driver.vehicle_type == "moto" else "moto"
        logger.info(f"\n--- MATCH TEST 3: Wrong Type ({wrong_type}) ---")
        matched = matching_service.find_available_drivers(
            db=db,
            pickup_latitude=lat,
            pickup_longitude=lon,
            ride_type=wrong_type,
            radius_km=5.0
        )
        logger.info(f"Found {len(matched)} drivers")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_matching()
