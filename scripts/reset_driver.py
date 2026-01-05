import sys
import os
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))
from app.core.database import SessionLocal
from app.models.driver import Driver

def reset_driver():
    db = SessionLocal()
    try:
        # Find the test driver (moto)
        driver = db.query(Driver).filter(Driver.vehicle_type == "moto").first()
        if driver:
            print(f"🔧 Resetting Driver {driver.id}...")
            driver.is_online = True
            driver.is_available = True
            db.commit()
            print("✅ Driver is now ONLINE and AVAILABLE.")
        else:
            print("❌ No moto driver found.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_driver()
