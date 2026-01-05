import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_columns():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("Checking users table...")
        
        # Add reputation_score
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reputation_score INTEGER DEFAULT 100"))
            print("Added reputation_score column.")
        except Exception as e:
            print(f"reputation_score might exist or error: {e}")
            
        # Add points
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0"))
            print("Added points column.")
        except Exception as e:
            print(f"points might exist or error: {e}")
            
        conn.commit()
    print("Migration complete.")

if __name__ == "__main__":
    add_columns()
