# Development Environment Setup Guide

This guide will help you set up your development environment for the Cameroon Traffic App.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Git** - Version control
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

2. **Node.js** (v18 or higher) - For React Native
   - Download: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

3. **Python** (v3.11 or higher) - For FastAPI backend
   - Download: https://www.python.org/downloads/
   - Verify: `python --version` or `python3 --version`

4. **Docker Desktop** - For PostgreSQL and Redis
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version` and `docker-compose --version`

### For Mobile Development

5. **Android Studio** (for Android development)
   - Download: https://developer.android.com/studio
   - Install Android SDK, Android SDK Platform, and Android Virtual Device
   - Set up ANDROID_HOME environment variable

6. **Xcode** (for iOS development, macOS only)
   - Download from Mac App Store
   - Install Xcode Command Line Tools: `xcode-select --install`

7. **React Native CLI**
   ```bash
   npm install -g react-native-cli
   ```

### Recommended Tools

- **VS Code** - Code editor
  - Extensions: Python, ESLint, Prettier, React Native Tools
- **Postman** or **Insomnia** - API testing
- **pgAdmin** - PostgreSQL GUI (optional)

---

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/[username]/cameroon-traffic-app.git
cd cameroon-traffic-app
```

### 2. Backend Setup

#### 2.1 Create Python Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update the following:
- `SECRET_KEY` - Generate a secure random key
- `JWT_SECRET_KEY` - Generate another secure random key
- Other settings as needed

#### 2.4 Start Database Services with Docker

```bash
# From project root
cd ..
docker-compose up -d postgres redis
```

Verify services are running:
```bash
docker-compose ps
```

#### 2.5 Initialize Database

```bash
cd backend
# Create database tables (will use Alembic migrations later)
python -c "from app.core.database import init_db; init_db()"
```

#### 2.6 Run Backend Server

```bash
uvicorn app.main:app --reload
```

The API should now be running at http://localhost:8000

Test it:
```bash
curl http://localhost:8000/api/v1/health
```

API documentation available at: http://localhost:8000/api/docs

### 3. Mobile App Setup

#### 3.1 Install Node Dependencies

```bash
cd mobile
npm install
```

#### 3.2 Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update:
- `API_BASE_URL` - Backend API URL (http://localhost:8000/api/v1 for local dev)
- `MAPBOX_ACCESS_TOKEN` - Your Mapbox token (see below)
- Firebase configuration (see below)

#### 3.3 Set Up Mapbox

1. Create account at https://www.mapbox.com/
2. Get your access token from https://account.mapbox.com/
3. Add token to `.env` file

#### 3.4 Set Up Firebase

1. Go to https://console.firebase.google.com/
2. Create a new project
3. Enable Authentication → Phone authentication
4. Enable Cloud Messaging
5. Add Android app (and iOS if needed)
6. Download `google-services.json` (Android) and place in `mobile/android/app/`
7. Download `GoogleService-Info.plist` (iOS) and place in `mobile/ios/`
8. Update `.env` with Firebase configuration

#### 3.5 Install iOS Dependencies (macOS only)

```bash
cd ios
pod install
cd ..
```

#### 3.6 Run Mobile App

**Android:**
```bash
# Start Metro bundler
npm start

# In another terminal, run Android app
npm run android
```

**iOS (macOS only):**
```bash
npm run ios
```

---

## Using Docker Compose (Recommended)

The easiest way to run the entire stack:

### 1. Configure Environment

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env

# Mobile
cp mobile/.env.example mobile/.env
# Edit mobile/.env
```

### 2. Start All Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL with PostGIS (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)

### 3. View Logs

```bash
docker-compose logs -f backend
```

### 4. Stop Services

```bash
docker-compose down
```

### 5. Reset Database

```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'app'`
- **Solution:** Make sure you're in the `backend` directory and virtual environment is activated

**Problem:** Database connection error
- **Solution:** Ensure PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in `.env`

**Problem:** Redis connection error
- **Solution:** Ensure Redis is running: `docker-compose ps`
- Check REDIS_URL in `.env`

### Mobile Issues

**Problem:** Metro bundler won't start
- **Solution:** Clear cache: `npm start -- --reset-cache`

**Problem:** Android build fails
- **Solution:** 
  - Clean build: `cd android && ./gradlew clean && cd ..`
  - Check ANDROID_HOME is set
  - Ensure Android SDK is installed

**Problem:** iOS build fails (macOS)
- **Solution:**
  - Clean build: `cd ios && rm -rf Pods && pod install && cd ..`
  - Open Xcode and clean build folder

**Problem:** "Unable to resolve module"
- **Solution:** 
  - Delete node_modules: `rm -rf node_modules`
  - Reinstall: `npm install`
  - Clear cache: `npm start -- --reset-cache`

### Docker Issues

**Problem:** Port already in use
- **Solution:** Stop conflicting service or change port in `docker-compose.yml`

**Problem:** Permission denied
- **Solution:** Run with sudo (Linux) or ensure Docker Desktop is running (Windows/macOS)

---

## Verify Installation

### Backend Checklist
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] PostgreSQL running (Docker)
- [ ] Redis running (Docker)
- [ ] Backend server starts without errors
- [ ] Health endpoint returns 200: http://localhost:8000/api/v1/health
- [ ] API docs accessible: http://localhost:8000/api/docs

### Mobile Checklist
- [ ] Node.js 18+ installed
- [ ] React Native CLI installed
- [ ] Dependencies installed
- [ ] Android Studio installed (for Android)
- [ ] Xcode installed (for iOS, macOS only)
- [ ] Mapbox token configured
- [ ] Firebase configured
- [ ] App builds and runs on emulator/simulator

---

## Next Steps

Once your environment is set up:

1. Read [PROJECT_DOCUMENTATION.md](../../PROJECT_DOCUMENTATION.md) for architecture overview
2. Check [PROGRESS.md](../../PROGRESS.md) for current development status
3. Review [CONTRIBUTING.md](../../CONTRIBUTING.md) for coding standards
4. Start with Week 3-4 tasks (Backend Foundation)

---

## Getting Help

If you encounter issues:
1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Create a new issue with:
   - Your OS and versions (Node, Python, etc.)
   - Error messages
   - Steps to reproduce

---

**Happy coding! 🚀**

