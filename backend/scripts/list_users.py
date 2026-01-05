import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User

def list_users():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    users = db.query(User).all()
    for u in users:
        print(f"ID: {u.id} | Name: {u.full_name} | Phone: {u.phone_number} | Pts: {u.points} | Rep: {u.reputation_score}")

if __name__ == "__main__":
    list_users()
