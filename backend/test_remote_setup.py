"""
Quick setup script to test remote database connection
Run this after setting up Supabase/Railway and updating .env
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test PostgreSQL connection"""
    print("🔍 Testing database connection...")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connected successfully!")
            
            # Test PostGIS
            try:
                result = conn.execute(text("SELECT PostGIS_version()"))
                version = result.scalar()
                print(f"✅ PostGIS enabled: {version}")
            except Exception as e:
                print(f"⚠️  PostGIS not enabled: {e}")
                print("   Run: CREATE EXTENSION IF NOT EXISTS postgis;")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check DATABASE_URL in .env file")
        print("   2. Ensure database is accessible (not behind firewall)")
        print("   3. Verify credentials are correct")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    
    try:
        import redis
        from app.core.config import settings
        
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis connected successfully!")
        
        # Test set/get
        r.set("test_key", "test_value")
        value = r.get("test_key")
        r.delete("test_key")
        print("✅ Redis read/write working!")
        
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check REDIS_URL in .env file")
        print("   2. Ensure Redis instance is running")
        print("   3. Verify credentials are correct")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    print("🔍 Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("\n💡 Create .env file:")
        print("   1. Copy .env.example to .env")
        print("   2. Update DATABASE_URL with your Supabase/Railway connection string")
        print("   3. Update REDIS_URL with your Upstash connection string")
        return False
    
    load_dotenv()
    
    database_url = os.getenv("DATABASE_URL", "")
    redis_url = os.getenv("REDIS_URL", "")
    
    if "localhost" in database_url:
        print("⚠️  DATABASE_URL points to localhost (Docker)")
        print("   Update with remote database URL (Supabase/Railway)")
        return False
    
    if "localhost" in redis_url:
        print("⚠️  REDIS_URL points to localhost (Docker)")
        print("   Update with remote Redis URL (Upstash)")
        return False
    
    if "[YOUR-PASSWORD]" in database_url or "[PASSWORD]" in database_url:
        print("❌ DATABASE_URL contains placeholder password!")
        print("   Replace [YOUR-PASSWORD] with actual password")
        return False
    
    if "[PASSWORD]" in redis_url or "[ENDPOINT]" in redis_url:
        print("❌ REDIS_URL contains placeholder values!")
        print("   Replace [PASSWORD] and [ENDPOINT] with actual values")
        return False
    
    print("✅ Environment file configured!")
    return True


def main():
    """Main setup verification"""
    print("=" * 60)
    print("🚀 Ehreezoh Remote Database Setup Verification")
    print("=" * 60)
    print()
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    print()
    
    # Test database
    db_ok = test_database_connection()
    
    # Test Redis
    redis_ok = test_redis_connection()
    
    print()
    print("=" * 60)
    
    if db_ok and redis_ok:
        print("✅ All connections successful!")
        print()
        print("Next steps:")
        print("  1. Run migrations: alembic upgrade head")
        print("  2. Start backend: uvicorn app.main:app --reload")
        print("  3. Visit: http://localhost:8000/api/docs")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Some connections failed!")
        print()
        print("See troubleshooting tips above.")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
