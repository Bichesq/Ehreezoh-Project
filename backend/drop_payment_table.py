from app.core.database import engine
from sqlalchemy import text

def drop_payment_table():
    try:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS payments CASCADE"))
            conn.commit()
            print("✅ Dropped payments table")
    except Exception as e:
        print(f"❌ Error dropping table: {e}")

if __name__ == "__main__":
    drop_payment_table()
