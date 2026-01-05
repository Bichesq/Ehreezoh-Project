
import logging
from sqlalchemy import text
from app.core.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_columns():
    with engine.connect() as conn:
        try:
            # Add reputation_score column
            logger.info("Adding reputation_score column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reputation_score INTEGER DEFAULT 100"))
            
            # Add points column
            logger.info("Adding points column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0"))
            
            conn.commit()
            logger.info("Successfully added missing columns to users table.")
            
        except Exception as e:
            logger.error(f"Error adding columns: {e}")
            raise

if __name__ == "__main__":
    add_columns()
