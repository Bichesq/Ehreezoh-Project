"""
Complete database cleanup - removes ALL objects
This will work even if schema reset didn't
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def complete_cleanup():
    """Drop everything in the database"""
    engine = create_engine(settings.DATABASE_URL)
    
    logger.info("🧹 Starting complete database cleanup...")
    
    with engine.connect() as conn:
        # Get all tables
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]
        
        logger.info(f"Found {len(tables)} tables to drop")
        
        # Drop all tables with CASCADE
        for table in tables:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                conn.commit()
                logger.info(f"  ✅ Dropped table: {table}")
            except Exception as e:
                logger.warning(f"  ⚠️  Error dropping {table}: {e}")
        
        # Drop all sequences
        result = conn.execute(text("""
            SELECT sequence_name FROM information_schema.sequences
            WHERE sequence_schema = 'public'
        """))
        sequences = [row[0] for row in result]
        
        for seq in sequences:
            try:
                conn.execute(text(f'DROP SEQUENCE IF EXISTS "{seq}" CASCADE'))
                conn.commit()
                logger.info(f"  ✅ Dropped sequence: {seq}")
            except Exception as e:
                logger.warning(f"  ⚠️  Error dropping {seq}: {e}")
        
        # Drop all views
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.views
            WHERE table_schema = 'public'
        """))
        views = [row[0] for row in result]
        
        for view in views:
            try:
                conn.execute(text(f'DROP VIEW IF EXISTS "{view}" CASCADE'))
                conn.commit()
                logger.info(f"  ✅ Dropped view: {view}")
            except Exception as e:
                logger.warning(f"  ⚠️  Error dropping {view}: {e}")
        
        # Drop all custom types
        result = conn.execute(text("""
            SELECT typname FROM pg_type 
            WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            AND typtype = 'e'
        """))
        types = [row[0] for row in result]
        
        for typ in types:
            try:
                conn.execute(text(f'DROP TYPE IF EXISTS "{typ}" CASCADE'))
                conn.commit()
                logger.info(f"  ✅ Dropped type: {typ}")
            except Exception as e:
                logger.warning(f"  ⚠️  Error dropping {typ}: {e}")
        
        # Verify PostGIS is still enabled
        try:
            result = conn.execute(text("SELECT PostGIS_version()"))
            version = result.scalar()
            logger.info(f"✅ PostGIS still enabled: {version}")
        except:
            logger.info("⚠️  Re-enabling PostGIS...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.commit()
            logger.info("✅ PostGIS enabled")
        
        logger.info("\n" + "="*60)
        logger.info("✅ Database cleanup complete!")
        logger.info("="*60)
        logger.info("\nNext step:")
        logger.info("  Run: alembic upgrade head")

if __name__ == "__main__":
    complete_cleanup()
