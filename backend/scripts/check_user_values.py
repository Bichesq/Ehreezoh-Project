import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User

def check_user():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Try to find Quincy
    user = db.query(User).filter(User.full_name.ilike("%Quincy%")).first()
    if user:
        print(f"User: {user.full_name}")
        print(f"Points: {user.points}")
        print(f"Reputation: {user.reputation_score}")
        print(f"To Dict: {user.to_dict()}")
    else:
        print("User Quincy not found")

if __name__ == "__main__":
    check_user()
