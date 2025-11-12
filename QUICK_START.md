# 🚀 Quick Start Guide

Get the Cameroon Traffic App running in 5 minutes!

## Prerequisites

- ✅ Node.js 18+
- ✅ Python 3.11+
- ✅ Docker Desktop
- ✅ Git

## Option 1: Automated Setup (Recommended)

### Windows
```bash
scripts\setup.bat
```

### macOS/Linux
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Option 2: Manual Setup

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/[username]/cameroon-traffic-app.git
cd cameroon-traffic-app

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
cd ..

# Mobile setup
cd mobile
npm install
cp .env.example .env
cd ..
```

### 2. Start Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Start backend (in new terminal)
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

### 3. Verify

```bash
# Test API
curl http://localhost:8000/api/v1/health

# Open API docs
# Visit: http://localhost:8000/api/docs
```

## Common Commands

### Backend

```bash
# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Lint code
flake8 app/

# Format code
black app/
```

### Mobile

```bash
# Start Metro bundler
cd mobile
npm start

# Run on Android
npm run android

# Run on iOS (macOS only)
npm run ios

# Run tests
npm test

# Lint code
npm run lint
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d
```

## Project Structure

```
cameroon-traffic-app/
├── 📚 Documentation
│   ├── PROJECT_DOCUMENTATION.md  # Complete technical docs
│   ├── PROGRESS.md               # Development tracker
│   ├── README.md                 # Project overview
│   ├── CONTRIBUTING.md           # Contribution guide
│   └── SETUP_COMPLETE.md         # Setup summary
│
├── 🔧 Backend (FastAPI)
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── api/                 # API routes
│   │   ├── core/                # Config & database
│   │   ├── models/              # Database models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── requirements.txt
│   └── Dockerfile
│
├── 📱 Mobile (React Native)
│   ├── src/                     # Source code
│   ├── package.json
│   └── tsconfig.json
│
├── 🐳 Infrastructure
│   ├── docker-compose.yml       # Docker services
│   └── .github/workflows/       # CI/CD
│
└── 📖 Guides
    └── docs/guides/SETUP.md     # Detailed setup
```

## API Endpoints

### Health Check
```bash
GET /api/v1/health
GET /api/v1/ping
```

### Authentication (Coming in Week 3-4)
```bash
POST /api/v1/auth/register
POST /api/v1/auth/login
```

### Incidents (Coming in Week 3-4)
```bash
POST   /api/v1/incidents          # Create incident
GET    /api/v1/incidents/nearby   # Get nearby incidents
PATCH  /api/v1/incidents/:id/vote # Vote on incident
DELETE /api/v1/incidents/:id      # Delete incident
POST   /api/v1/incidents/:id/report # Report abuse
```

### User (Coming in Week 3-4)
```bash
GET   /api/v1/user/profile        # Get profile
PATCH /api/v1/user/settings       # Update settings
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/traffic_app
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### Mobile (.env)
```env
API_BASE_URL=http://localhost:8000/api/v1
MAPBOX_ACCESS_TOKEN=your-mapbox-token
FIREBASE_PROJECT_ID=your-firebase-project-id
```

## Troubleshooting

### Backend won't start
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check if port 8000 is available
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Mobile build fails
```bash
# Clear cache
npm start -- --reset-cache

# Reinstall dependencies
rm -rf node_modules
npm install

# Android: Clean build
cd android && ./gradlew clean && cd ..
```

### Database connection error
```bash
# Restart Docker services
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

## Next Steps

1. ✅ Complete setup (you are here!)
2. 📝 Read [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)
3. 📊 Check [PROGRESS.md](PROGRESS.md) for current tasks
4. 🔧 Start Week 3-4: Backend Foundation
5. 📱 Continue to Week 5-6: Mobile App Core

## Resources

- **API Docs:** http://localhost:8000/api/docs
- **Setup Guide:** [docs/guides/SETUP.md](docs/guides/SETUP.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Progress:** [PROGRESS.md](PROGRESS.md)

## Getting Help

1. Check [docs/guides/SETUP.md](docs/guides/SETUP.md) for detailed troubleshooting
2. Review [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for architecture
3. Search existing issues on GitHub
4. Create a new issue with error details

---

**Ready to build? Let's make Cameroon roads safer! 🚗🇨🇲**

