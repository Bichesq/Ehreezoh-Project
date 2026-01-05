# Ehreezoh - Quick Setup Guide

## Prerequisites Checklist

Before running the backend, ensure you have:

- [ ] **Docker Desktop** installed and running
- [ ] **Python 3.11+** installed
- [ ] **Git** installed

## Step-by-Step Setup

### 1. Start Docker Desktop

**Windows:**
- Open Docker Desktop from Start Menu
- Wait for the whale icon to appear in system tray
- Ensure it says "Docker Desktop is running"

**Verify:**
```bash
docker --version
docker-compose --version
```

### 2. Start Database Services

```bash
cd "c:\Users\biche\Ehreezoh Project"
docker-compose up -d
```

**Expected output:**
```
✔ Container postgres  Started
✔ Container redis     Started
```

### 3. Set Up Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env and update:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ehreezoh
```

### 5. Run Database Migrations

```bash
# Still in backend directory
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Initial schema
```

### 6. Verify Database

```bash
# Connect to database
docker exec -it postgres psql -U postgres -d ehreezoh

# List tables
\dt

# Should see:
# - users
# - drivers
# - rides
# - payments
# - driver_ratings
# - passenger_ratings

# Exit
\q
```

### 7. Start Backend Server

```bash
# Still in backend directory with venv activated
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 8. Test API

Open browser: http://localhost:8000/api/docs

You should see the Swagger UI with available endpoints.

## Troubleshooting

### Docker Desktop Not Running

**Symptom:** `unable to get image` error

**Fix:**
1. Start Docker Desktop
2. Wait 30 seconds
3. Run `docker-compose up -d` again

### Port Already in Use

**Symptom:** `port 5432 is already allocated`

**Fix:**
```bash
# Stop existing containers
docker-compose down

# Start again
docker-compose up -d
```

### Alembic Not Found

**Symptom:** `alembic: command not found`

**Fix:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

Once setup is complete:

1. **Create Firebase Project** - For authentication
2. **Get Mapbox API Key** - For maps
3. **Implement Auth Endpoints** - User registration/login

See [walkthrough.md](file:///C:/Users/biche/.gemini/antigravity/brain/e32a7183-a1da-40b9-bfc7-eea853009ad1/walkthrough.md) for detailed progress and next tasks.
