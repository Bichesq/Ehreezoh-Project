import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env from backend directory
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
load_dotenv(os.path.join(backend_dir, '.env'))

# Add backend directory to path
sys.path.append(backend_dir)

from app.core.config import settings
from app.models.user import User

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_status():
    db = SessionLocal()
    try:
        # Get last 5 users
        users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        print(f"found {len(users)} users")
        for user in users:
            print(f"---")
            print(f"User: {user.full_name}")
            print(f"Phone: {user.phone_number}")
            print(f"Is Driver: {user.is_driver}")
            print(f"Is Passenger: {user.is_passenger}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_status()
