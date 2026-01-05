# Ehreezoh Backend - Remote Database Setup

## Quick Start (No Docker Required!)

### 1. Set Up Remote Databases (15 minutes)

**PostgreSQL (Supabase - Recommended):**
1. Go to https://supabase.com and sign up
2. Create new project: `ehreezoh-dev`
3. Copy connection string from Settings → Database 
 ### connect to Neon
 npx neonctl@latest init
4. PostGIS is already enabled!

**Redis (Upstash):**
1. Go to https://upstash.com and sign up
2. Create database: `ehreezoh-redis`
3. Copy Redis URL from dashboard

### 2. Configure Environment

```bash
cd backend

# Copy example file
copy .env.example .env

# Edit .env and update:
# - DATABASE_URL (from Supabase)
# - REDIS_URL (from Upstash)
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/Scripts/activate

# Install packages
pip install -r requirements.txt
```

### 4. Test Connection

```bash
python test_remote_setup.py
```

**Expected output:**
```
✅ Database connected successfully!
✅ PostGIS enabled: 3.3.2
✅ Redis connected successfully!
✅ All connections successful!
```

### 5. Run Migrations

```bash
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
```

### 6. Start Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
## 7. Open Firewall
netsh advfirewall firewall add rule name="Ehreezoh Backend" dir=in action=allow protocol=TCP localport=8000

Visit: http://localhost:8000/api/docs

---

## Detailed Setup Guides

- **Remote Database Setup:** See [remote_database_setup.md](file:///C:/Users/biche/.gemini/antigravity/brain/e32a7183-a1da-40b9-bfc7-eea853009ad1/remote_database_setup.md)
- **Full Walkthrough:** See [walkthrough.md](file:///C:/Users/biche/.gemini/antigravity/brain/e32a7183-a1da-40b9-bfc7-eea853009ad1/walkthrough.md)

---

## Troubleshooting

### Connection Failed

Run the test script for detailed diagnostics:
```bash
python test_remote_setup.py
```

### PostGIS Not Enabled

In Supabase SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_version();
```

### Migrations Failed

Check database URL is correct:
```bash
# Should NOT contain localhost
echo %DATABASE_URL%
```

---

## Free Tier Limits

- **Supabase:** 500MB database, 2GB bandwidth/month
- **Upstash:** 10,000 commands/day
- **Perfect for development!**

---

**Next:** Implement Firebase Authentication (4-6 hours)
