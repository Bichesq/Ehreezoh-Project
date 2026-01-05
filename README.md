# 🚗 Ehreezoh - Comprehensive Mobility Platform

> Cameroon's ride-hailing and traffic intelligence platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React Native](https://img.shields.io/badge/React%20Native-0.73-blue.svg)](https://reactnative.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

A comprehensive mobility platform for Cameroon combining **on-demand ride-hailing** (moto-taxis and cars) with **community-driven traffic intelligence**, empowering both drivers and passengers while improving urban transportation.

## 🎯 Mission

Become Cameroon's leading mobility platform by providing affordable, safe, and reliable transportation while fostering a community that actively contributes to better traffic conditions.

## 📱 Features

### 🚗 CO-PRIMARY: Ride-Hailing Platform (50% of MVP)

**For Passengers:**
- 🚕 **Request Rides** - Moto-taxis, economy cars, and comfort cars
- 💰 **Fare Negotiation** - InDrive-style transparent pricing
- 📍 **Real-time Tracking** - Track your driver's location and ETA
- 🛣️ **Intelligent Route Selection** - Choose routes that avoid traffic and accidents
- 💳 **Flexible Payments** - Cash, MTN Mobile Money, Orange Money
- ⭐ **Driver Ratings** - Rate and review your driver
- 📜 **Trip History** - View all past rides and receipts
- 🆘 **Safety Features** - Emergency SOS, trip sharing with contacts
- 🌍 **Bilingual** - Full support for French and English

**For Drivers:**
- 💼 **Flexible Earnings** - Work when you want, earn on your terms
- 📱 **Easy Onboarding** - Simple registration and verification
- 💵 **Instant Payouts** - Cash out to Mobile Money anytime
- 🗺️ **Smart Navigation** - Traffic-aware turn-by-turn directions
- 💰 **Earn Rewards** - Get 100 XAF for each verified incident report
- 📊 **Earnings Dashboard** - Track your daily, weekly, monthly income
- 🤝 **Fair Commission** - Only 12-15% (vs Uber's 25%)
- ⭐ **Passenger Ratings** - Rate passengers for better matches
- 🏍️ **Moto-Taxi Support** - Designed for Cameroon's most popular transport

### 🗺️ CO-PRIMARY: Intelligent Route Guidance (50% of MVP)

**Real-Time Intelligence:**
- 📍 **Crowdsourced Incident Reports** - Traffic, accidents, road hazards, police checkpoints*
- 📸 **Photo Evidence** - Upload photos for verification
- 👥 **Community Verification** - Upvote/downvote system for credibility
- 🔴 **Live Incident Map** - See real-time traffic problems on your route
- ⏰ **Auto-Expiration** - Stale incidents removed automatically

**Smart Routing:**
- 🧠 **Route Scoring** - Each route scored based on incident severity
- 🛣️ **Alternative Routes** - Avoid accidents, traffic jams, and blockages
- 📊 **Predictive Routing** - Learn traffic patterns (e.g., "Avenue Kennedy has traffic 7-9am Mon-Fri")
- 🔔 **Proactive Alerts** - Get warned BEFORE you hit traffic
- ⚡ **Real-Time Rerouting** - Auto-recalculate if new incident reported
- 🎯 **Multi-Criteria Options** - "Safest Route" vs "Fastest Route" vs "Balanced"

**Driver Benefits:**
- 💰 **Earn 100 XAF** per verified incident report (verified drivers only)
- 🗺️ **Incident Heatmap** - See where to avoid and where to position for rides
- 📈 **Historical Hotspots** - Optimize your location for maximum earnings
- 🚧 **Police Checkpoint Awareness** (feature ready, awaiting legal approval)*

**Why It Matters:**
- 🇨🇲 **Cameroon-First** - No official traffic data? Community fills the gap
- 🔄 **Offline Support** - Recent incidents cached for offline access
- 📱 **Cultural Fit** - Formalizes WhatsApp traffic groups into one app
- ⚡ **Time & Money Savings** - Avoid jams, get passengers faster

*Police checkpoint feature built but permission-gated. Only special users can access until legal approval.

### Coming Soon (Phase 2+)
- 📅 Scheduled rides and reservations
- 🚗 Ride-sharing (carpooling)
- 💬 In-app chat
- 🏢 Corporate accounts
- 🎁 Loyalty rewards program
- 📦 Delivery services
- 🍔 Food delivery integration
- 🍎 iOS version

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              PASSENGER APP (React Native)                │
│   Request Rides | Track Driver | Payments | History     │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTPS/WSS
┌─────────────────────────────────────────────────────────┐
│               DRIVER APP (React Native)                  │
│   Accept Rides | Navigation | Earnings | Profile        │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTPS/WSS
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│   Ride Matching | Payments | Real-time Tracking         │
│   - Python 3.11+ | SQLAlchemy + GeoAlchemy2             │
└─────────────────────────────────────────────────────────┘
                          ↕
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ PostgreSQL + │  │    Redis     │  │ Mobile Money │
│   PostGIS    │  │ (Locations)  │  │     APIs     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 🛠️ Technology Stack

### Mobile Apps (Passenger & Driver)
- **Framework:** React Native 0.73+ (shared codebase)
- **Language:** TypeScript
- **State Management:** Redux Toolkit + RTK Query
- **Maps & Navigation:** Mapbox Maps SDK
- **Real-time Location:** Background geolocation tracking
- **Offline Storage:** WatermelonDB
- **Navigation:** React Navigation 6
- **i18n:** react-i18next (French/English)
- **Payments:** Mobile Money integration components

### Backend
- **Framework:** FastAPI 0.104+ (Python 3.11+)
- **Database:** PostgreSQL 15 + PostGIS 3.3 (geospatial queries)
- **ORM:** SQLAlchemy 2.0 + GeoAlchemy2
- **Caching:** Redis 7+ (driver locations, ride queue)
- **Authentication:** Firebase Admin SDK
- **WebSocket:** FastAPI WebSockets (real-time tracking)
- **Task Queue:** Celery + RabbitMQ (payments, notifications)
- **Payment APIs:** MTN MoMo, Orange Money, Campay

### Infrastructure
- **Hosting:** DigitalOcean / AWS
- **CDN:** Cloudflare
- **Monitoring:** Sentry + Firebase Analytics
- **CI/CD:** GitHub Actions
- **Containerization:** Docker + Docker Compose

## 📂 Project Structure

```
ehreezoh/
├── mobile/                 # React Native apps (Passenger + Driver)
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── screens/       # Screen components
│   │   │   ├── passenger/ # Passenger-specific screens
│   │   │   ├── driver/    # Driver-specific screens
│   │   │   └── shared/    # Shared screens (auth, profile)
│   │   ├── navigation/    # Navigation configuration
│   │   ├── store/         # Redux store and slices
│   │   │   ├── rides/     # Ride management
│   │   │   ├── payments/  # Payment handling
│   │   │   ├── location/  # Location tracking
│   │   │   └── traffic/   # Traffic reporting
│   │   ├── services/      # API services
│   │   │   ├── rideApi.ts
│   │   │   ├── paymentApi.ts
│   │   │   └── trafficApi.ts
│   │   ├── utils/         # Utility functions
│   │   ├── i18n/          # Translations (en, fr)
│   │   └── types/         # TypeScript types
│   ├── android/           # Android native code
│   ├── ios/               # iOS native code
│   ├── package.json
│   └── tsconfig.json
│
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   │   ├── rides.py  # Ride-hailing endpoints
│   │   │   ├── drivers.py
│   │   │   ├── payments.py
│   │   │   ├── ratings.py
│   │   │   ├── incidents.py  # Traffic reporting
│   │   │   └── auth.py
│   │   ├── models/       # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── driver.py
│   │   │   ├── ride.py
│   │   │   ├── payment.py
│   │   │   └── incident.py
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   │   ├── matching.py  # Driver-passenger matching
│   │   │   ├── fare.py      # Fare calculation
│   │   │   ├── payment.py   # Payment processing
│   │   │   └── notification.py
│   │   ├── core/         # Config, security, database
│   │   ├── utils/        # Utility functions
│   │   └── main.py       # FastAPI app entry point
│   ├── alembic/          # Database migrations
│   ├── tests/            # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── architecture/     # Architecture diagrams
│   └── guides/           # Development guides
│
├── .github/              # GitHub Actions workflows
│   └── workflows/
│
├── docker-compose.yml    # Local development setup
├── .gitignore
├── PROJECT_DOCUMENTATION.md  # Comprehensive project docs
├── PROGRESS.md           # Development progress tracker
└── README.md             # This file
```

## 🚀 Getting Started

### Quick Start (5 minutes)

**Automated Setup:**
```bash
# Windows
scripts\setup.bat

# macOS/Linux
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Manual Setup:**
```bash
# 1. Clone repository
git clone https://github.com/[username]/cameroon-traffic-app.git
cd cameroon-traffic-app

# 2. Backend setup
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows: venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
cd ..

# 3. Mobile setup
cd mobile
npm install
cp .env.example .env
cd ..

# 4. Start services
docker-compose up -d

# 5. Start backend
cd backend
uvicorn app.main:app --reload
```

**Verify Installation:**
```bash
curl http://localhost:8000/api/v1/health
# Visit: http://localhost:8000/api/docs
```

### Detailed Guides

- **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
- **[docs/guides/SETUP.md](docs/guides/SETUP.md)** - Complete setup guide with troubleshooting
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - What has been created and next steps

## 📖 Documentation

- **[Project Documentation](PROJECT_DOCUMENTATION.md)** - Comprehensive technical documentation
- **[Development Progress](PROGRESS.md)** - Week-by-week progress tracker
- **[API Documentation](docs/api/README.md)** - REST API and WebSocket specifications
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Mobile Tests
```bash
cd mobile
npm test
```

## 🌍 Cameroon-Specific Features

### Ride-Hailing
- **Moto-Taxi Priority:** Designed for Cameroon's most popular transport mode
- **Fare Negotiation:** InDrive-style transparent pricing (culturally appropriate)
- **Mobile Money Integration:** MTN Mobile Money, Orange Money (40% penetration)
- **Cash Payments:** Primary payment method (80% of transactions)
- **Low Commission:** 12-15% vs Uber's 25% (fair to drivers)
- **Instant Payouts:** Drivers cash out anytime to Mobile Money
- **Local Language:** French, English, and Pidgin support
- **Union Partnerships:** Work with existing moto-taxi unions

### Traffic Intelligence
- **Bilingual Support:** French and English throughout
- **Low Bandwidth Optimization:** Aggressive caching and compression
- **Offline-First:** Core features work without internet
- **Data Cost Awareness:** Minimal data usage, WiFi-only options
- **Local Context:** Designed for Cameroon's road conditions

### Market Positioning
- **Cameroon-First:** Not an international expansion, built for Cameroon
- **Community-Driven:** Drivers and passengers shape the platform
- **Affordable:** Competitive pricing for passengers, fair earnings for drivers
- **Safe:** Driver verification, ratings, emergency features

## 🔒 Privacy & Security

- **Privacy-First:** Minimal data collection, no location tracking
- **Encrypted:** TLS 1.3 for all communications
- **Anonymous Reporting:** Optional anonymous incident reporting
- **Data Retention:** Auto-delete expired incidents
- **GDPR-Inspired:** User rights to access, export, and delete data

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Contact

- **Email:** support@trafficcm.app
- **GitHub Issues:** [Report bugs or request features](https://github.com/[username]/cameroon-traffic-app/issues)

## 🙏 Acknowledgments

- Built for the people of Cameroon 🇨🇲
- Powered by open-source technologies
- Inspired by community-driven traffic apps worldwide

## 📊 Project Status

**Current Phase:** Week 1-2 (Setup & Planning) ✅ COMPLETE
**Next Phase:** Week 3-5 (Backend Foundation - Ride-Hailing Core)
**MVP Target:** March 10, 2026 (16 weeks)
**Progress:** 12% complete

### Development Timeline
- ✅ **Week 1-2:** Setup & Planning (COMPLETE)
- ⏳ **Week 3-5:** Backend Foundation - Ride-Hailing Core
- ⏳ **Week 6-8:** Mobile Apps - Passenger & Driver
- ⏳ **Week 9-11:** Payments & Traffic Reporting
- ⏳ **Week 12-14:** Real-time Features & Testing
- ⏳ **Week 15-16:** Launch Preparation

See [PROGRESS.md](PROGRESS.md) for detailed development status.

## 🎯 Why Ehreezoh?

**For Passengers:**
- 💰 **Affordable** - Transparent pricing, fare negotiation
- 🚀 **Fast** - Moto-taxis beat traffic congestion
- 🔒 **Safe** - Driver verification, ratings, trip sharing
- 💳 **Flexible** - Pay cash or Mobile Money

**For Drivers:**
- 💵 **Fair Earnings** - Low 12-15% commission
- ⚡ **Instant Payouts** - Cash out anytime
- 📱 **Easy to Use** - Simple app, no complexity
- 🤝 **Respectful** - Drivers are partners, not employees

**For Cameroon:**
- 🇨🇲 **Local First** - Built for Cameroon, by Cameroonians
- 🚦 **Better Traffic** - Community-driven traffic intelligence
- 💼 **Job Creation** - Empower thousands of drivers
- 🌍 **Economic Growth** - Efficient transportation = economic development

---

**Made with ❤️ for Cameroon 🇨🇲**
