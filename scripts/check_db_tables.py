import sys
import os
from sqlalchemy import inspect

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')))

from app.core.database import engine

def check_tables():
    print("Connecting to database...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Found tables:")
    for table in tables:
        print(f"- {table}")
    
    required = ["users", "drivers", "rides", "payments", "driver_ratings", "passenger_ratings"]
    missing = [t for t in required if t not in tables]
    
    if missing:
        print(f"\n❌ Missing required tables: {missing}")
        # Note: 'driver_ratings' might be named differently in models, checking schema would be better but this is a good start
    else:
        print("\n✅ All core tables found.")

if __name__ == "__main__":
    check_tables()
