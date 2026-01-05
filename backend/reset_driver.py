from app.core.database import SessionLocal
from app.models.user import User
from app.models.driver import Driver

def reset_driver(phone_number: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            print("User not found")
            return

        driver = db.query(Driver).filter(Driver.user_id == user.id).first()
        if not driver:
            print("Driver not found")
            return

        driver.is_available = True
        driver.is_online = True # Optional
        db.commit()
        print(f"✅ Driver {phone_number} reset to AVAILABLE and ONLINE.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_driver("+237611223344")
