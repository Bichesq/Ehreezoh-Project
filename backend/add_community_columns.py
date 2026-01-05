"""
Script to add missing community columns to users table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for async drivers
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

ALTER_COMMANDS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS trust_score INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_reports INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_people_helped INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_report_date TIMESTAMP",
]

with engine.connect() as conn:
    for cmd in ALTER_COMMANDS:
        try:
            conn.execute(text(cmd))
            print(f"✅ {cmd[:50]}...")
        except Exception as e:
            print(f"⚠️ {cmd[:50]}... - {e}")
    conn.commit()
    print("Done!")
