import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_columns():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('users')]
    print(f"User columns: {columns}")
    
    if 'reputation_score' in columns:
        print("reputation_score EXISTS")
    else:
        print("reputation_score MISSING")

if __name__ == "__main__":
    check_columns()
