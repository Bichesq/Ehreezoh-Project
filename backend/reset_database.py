"""
Reset database - Drop all tables and run fresh migrations
WARNING: This will delete all data!
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """Drop all tables and alembic version"""
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("Connecting to database...")
    
    with engine.connect() as conn:
        # Drop all tables in public schema
        logger.info("Dropping all tables...")
        
        # Drop tables in correct order (respecting foreign keys)
        tables = [
            'passenger_ratings',
            'driver_ratings',
            'payments',
            'rides',
            'drivers',
            'users',
            'alembic_version'
        ]
        
        for table in tables:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
                conn.commit()
                logger.info(f"✅ Dropped table: {table}")
            except Exception as e:
                logger.warning(f"⚠️  Could not drop {table}: {e}")
        
        logger.info("✅ Database reset complete!")
        logger.info("\nNext steps:")
        logger.info("  1. Run: alembic upgrade head")
        logger.info("  2. Start server: uvicorn app.main:app --reload")

if __name__ == "__main__":
    print("=" * 60)
    print("⚠️  WARNING: This will delete ALL data in the database!")
    print("=" * 60)
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        reset_database()
    else:
        print("❌ Cancelled")
