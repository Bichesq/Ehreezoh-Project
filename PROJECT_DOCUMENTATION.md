# Ehreezoh - Comprehensive Mobility Platform Documentation

**Project Name:** Ehreezoh (Cameroon Mobility Platform)
**Project Start Date:** November 11, 2025
**Target MVP Completion:** March 10, 2026 (16 weeks)
**Project Status:** In Development - Strategic Pivot Complete

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Design](#architecture-design)
4. [Database Schema](#database-schema)
5. [API Specification](#api-specification)
6. [UI/UX Design Principles](#uiux-design-principles)
7. [Cameroon-Specific Considerations](#cameroon-specific-considerations)
8. [Safety & Ethical Guidelines](#safety--ethical-guidelines)
9. [Development Phases](#development-phases)
10. [Deployment Strategy](#deployment-strategy)

---

## Project Overview

### Mission
Build a comprehensive mobility platform for Cameroon that combines on-demand ride-hailing services with community-driven traffic intelligence, empowering both drivers and passengers while improving urban transportation efficiency and safety.

### Vision
Become Cameroon's leading mobility platform by providing affordable, safe, and reliable transportation while fostering a community that actively contributes to better traffic conditions.

### Core Value Propositions

**For Passengers:**
- Affordable, transparent ride-hailing with fare negotiation
- Real-time driver tracking and ETA
- Multiple payment options (Mobile Money, cash)
- Safety features (driver ratings, trip sharing)
- Traffic-aware routing

**For Drivers:**
- Flexible earning opportunities
- Low commission rates (competitive with Uber/Bolt)
- Instant payment via Mobile Money
- Moto-taxi and car driver support
- Fair rating system

**For the Community:**
- Real-time traffic intelligence
- Collaborative incident reporting
- Safer, more efficient commutes

### MVP Features (Phase 1) - Prioritized

#### PRIMARY: Ride-Hailing Platform (70% of MVP effort)

**Passenger App:**
- ✅ Request rides with pickup/destination selection
- ✅ Real-time driver matching and tracking
- ✅ Fare estimation and negotiation (InDrive-style)
- ✅ Multiple ride types (moto-taxi, economy car, comfort car)
- ✅ In-app payment (Mobile Money: MTN, Orange)
- ✅ Trip history and receipts
- ✅ Driver ratings and reviews
- ✅ Emergency SOS button
- ✅ Trip sharing (share ETA with contacts)

**Driver App:**
- ✅ Accept/reject ride requests
- ✅ View passenger details and destination
- ✅ Counter-offer fare (negotiation)
- ✅ Turn-by-turn navigation
- ✅ Earnings dashboard
- ✅ Instant cashout to Mobile Money
- ✅ Passenger ratings
- ✅ Online/offline toggle

**Backend:**
- ✅ Real-time driver-passenger matching algorithm
- ✅ Geospatial queries for nearby drivers
- ✅ Fare calculation engine
- ✅ Payment processing (Mobile Money APIs)
- ✅ Trip tracking and history
- ✅ Rating and review system
- ✅ Driver verification and onboarding

#### SECONDARY: Traffic Intelligence (30% of MVP effort)

- ✅ View traffic incidents on map (both apps)
- ✅ Report incidents (traffic jam, accident, road hazard)
- ✅ Community verification (upvote/downvote)
- ✅ Traffic-aware routing suggestions
- ✅ Push notifications for route incidents

### Excluded from MVP (Phase 2+)
- ❌ Police checkpoint reporting (pending legal review)
- ❌ Scheduled rides / ride reservations
- ❌ Corporate accounts for businesses
- ❌ Driver referral program
- ❌ In-app chat between driver and passenger
- ❌ Multi-stop rides
- ❌ Ride-sharing (carpooling multiple passengers)
- ❌ Delivery services
- ❌ Advanced analytics dashboard for drivers
- ❌ Loyalty/rewards program

---

## Technology Stack

### Mobile Applications (Dual Apps)

**Passenger App & Driver App** (Shared codebase with role-based UI)
- **Framework:** React Native 0.73+
- **Language:** TypeScript
- **State Management:** Redux Toolkit + RTK Query
- **Navigation:** React Navigation 6
- **Maps:** Mapbox Maps SDK for React Native
- **Real-time Location:** @react-native-community/geolocation + background tracking
- **Offline Storage:** AsyncStorage + WatermelonDB
- **Image Handling:** react-native-image-picker + react-native-compressor
- **Push Notifications:** @react-native-firebase/messaging
- **Internationalization:** react-i18next
- **HTTP Client:** Axios
- **WebSocket:** Socket.io-client (real-time ride tracking)
- **Payment UI:** Custom Mobile Money integration components

### Backend
- **Framework:** FastAPI 0.104+ (Python 3.11+)
- **ASGI Server:** Uvicorn
- **Database ORM:** SQLAlchemy 2.0+ with GeoAlchemy2
- **Database:** PostgreSQL 15+ with PostGIS 3.3+
- **Caching:** Redis 7+ (driver locations, active rides)
- **Authentication:** Firebase Admin SDK
- **Image Storage:** AWS S3 / Cloudinary / Local (configurable)
- **WebSocket:** FastAPI WebSockets + Socket.io (ride tracking, driver matching)
- **Task Queue:** Celery (payment processing, notifications, matching algorithm)
- **Validation:** Pydantic v2
- **Migration:** Alembic
- **Payment Processing:** Custom Mobile Money API integrations

### Infrastructure & DevOps
- **Hosting:** DigitalOcean / AWS (scalable for real-time matching)
- **CDN:** Cloudflare
- **Monitoring:** Sentry (error tracking)
- **Analytics:** Firebase Analytics + Mixpanel (ride metrics)
- **CI/CD:** GitHub Actions
- **Container:** Docker + Docker Compose
- **Load Balancing:** Nginx / AWS ALB

### Third-Party Services
- **Authentication:** Firebase Authentication (Phone Auth)
- **Push Notifications:** Firebase Cloud Messaging (FCM)
- **Maps & Navigation:** Mapbox (primary), OpenStreetMap (fallback)
- **SMS Verification:** Twilio / Africa's Talking
- **Payment Gateways:**
  - **MTN Mobile Money:** MTN MoMo API
  - **Orange Money:** Orange Money API
  - **Campay:** Payment aggregator (MTN + Orange + Express Union)
  - **Monetbil:** Alternative aggregator
- **Background Jobs:** Celery + Redis
- **Real-time Database:** Redis (driver locations, ride queue)

---

## Architecture Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PASSENGER APP (React Native)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Request Ride │  │  Track Ride  │  │   Payments   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Traffic Map  │  │    History   │  │   Profile    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                ↕ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────────┐
│                     DRIVER APP (React Native)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Accept Rides │  │  Navigation  │  │   Earnings   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Traffic Map  │  │    History   │  │   Profile    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                ↕ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer (Nginx)               │
└─────────────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Ride API    │  │  Payment API │  │  Traffic API │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  WebSocket   │  │ Matching Svc │  │   Auth Svc   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                ↕
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ PostgreSQL + │  │    Redis     │  │   Firebase   │  │ Mobile Money │
│   PostGIS    │  │ (Locations)  │  │    (Auth)    │  │     APIs     │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
        ↕                 ↕
┌──────────────┐  ┌──────────────┐
│    Celery    │  │   RabbitMQ   │
│   Workers    │  │  (Queue)     │
└──────────────┘  └──────────────┘
```

### Data Flow

#### Ride Request Flow (Primary Feature)
1. **Passenger requests ride:**
   - Select pickup/destination on map
   - Choose ride type (moto, economy, comfort)
   - View estimated fare
   - Submit request

2. **Backend matching algorithm:**
   - Query Redis for nearby online drivers (geospatial)
   - Filter by ride type and availability
   - Calculate distance and ETA for each driver
   - Send ride request to top 5 drivers via FCM

3. **Driver receives request:**
   - Push notification with passenger details
   - View pickup location and destination
   - See offered fare
   - Accept, reject, or counter-offer

4. **Ride accepted:**
   - WebSocket establishes real-time connection
   - Driver location streamed to passenger every 3 seconds
   - Passenger sees driver approaching with ETA
   - Both apps show trip details

5. **Trip in progress:**
   - Driver navigates using Mapbox
   - Real-time location updates via WebSocket
   - Traffic incidents shown on route
   - Passenger can share trip with contacts

6. **Trip completion:**
   - Driver marks trip as complete
   - Fare calculation (time + distance)
   - Payment processed via Mobile Money API
   - Both parties rate each other
   - Receipt generated and stored

#### Traffic Reporting Flow (Secondary Feature)
1. User (driver or passenger) reports incident
2. Photo compressed and uploaded
3. Backend validates and stores in PostgreSQL
4. Redis cache updated
5. WebSocket broadcasts to nearby users
6. Incident shown on both passenger and driver maps
7. Community can upvote/downvote

#### Real-time Driver Location Updates
1. Driver app sends location every 3 seconds (when online)
2. Backend updates Redis geospatial index
3. Location stored with TTL (30 seconds)
4. Matching algorithm queries Redis for nearby drivers
5. During active ride, location streamed to passenger via WebSocket

### Security Architecture

- **Transport:** TLS 1.3 (HTTPS/WSS)
- **Authentication:** Firebase JWT tokens
- **Authorization:** Role-based access control (RBAC)
- **Data Encryption:** AES-256 for sensitive data at rest
- **Rate Limiting:** Redis-based token bucket
- **Input Validation:** Pydantic models + sanitization
- **CORS:** Restricted to mobile app origins
- **SQL Injection:** SQLAlchemy ORM (parameterized queries)

---

## Database Schema

### PostgreSQL Tables

#### 1. Users Table (Base for all users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    phone_hash VARCHAR(255) UNIQUE NOT NULL, -- bcrypt hash
    firebase_uid VARCHAR(128) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(255),
    profile_photo_url VARCHAR(500),
    language_preference VARCHAR(5) DEFAULT 'fr', -- 'fr' or 'en'

    -- User roles (can be both passenger and driver)
    is_passenger BOOLEAN DEFAULT true,
    is_driver BOOLEAN DEFAULT false,

    -- Traffic reporting (legacy feature)
    trust_score DECIMAL(3,2) DEFAULT 0.00,
    total_reports INT DEFAULT 0,
    verified_reports INT DEFAULT 0,
    upvotes_received INT DEFAULT 0,
    downvotes_received INT DEFAULT 0,

    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_banned BOOLEAN DEFAULT false,
    is_verified BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX idx_users_phone_hash ON users(phone_hash);
CREATE INDEX idx_users_is_driver ON users(is_driver) WHERE is_driver = true;
```

#### 2. Drivers Table (Extended profile for drivers)
```sql
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Driver details
    driver_license_number VARCHAR(50) UNIQUE NOT NULL,
    driver_license_photo_url VARCHAR(500),
    national_id_number VARCHAR(50),
    national_id_photo_url VARCHAR(500),

    -- Vehicle information
    vehicle_type VARCHAR(20) NOT NULL, -- 'moto', 'economy_car', 'comfort_car'
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    vehicle_year INT,
    vehicle_color VARCHAR(30),
    vehicle_plate_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_photo_url VARCHAR(500),

    -- Driver status
    is_online BOOLEAN DEFAULT false,
    is_available BOOLEAN DEFAULT true, -- Can accept rides
    is_verified BOOLEAN DEFAULT false, -- Admin verified
    verification_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    verification_notes TEXT,

    -- Performance metrics
    total_rides INT DEFAULT 0,
    completed_rides INT DEFAULT 0,
    cancelled_rides INT DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_earnings DECIMAL(10,2) DEFAULT 0.00,

    -- Current location (updated frequently)
    current_location GEOGRAPHY(POINT, 4326),
    current_latitude DECIMAL(10, 8),
    current_longitude DECIMAL(11, 8),
    last_location_update TIMESTAMP,

    -- Availability
    accepts_moto_requests BOOLEAN DEFAULT true,
    accepts_car_requests BOOLEAN DEFAULT true,
    max_pickup_distance_km INT DEFAULT 5,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    last_online_at TIMESTAMP
);

CREATE INDEX idx_drivers_user_id ON drivers(user_id);
CREATE INDEX idx_drivers_is_online ON drivers(is_online) WHERE is_online = true;
CREATE INDEX idx_drivers_is_available ON drivers(is_available) WHERE is_available = true;
CREATE INDEX idx_drivers_current_location ON drivers USING GIST(current_location);
CREATE INDEX idx_drivers_vehicle_type ON drivers(vehicle_type);
CREATE INDEX idx_drivers_verification_status ON drivers(verification_status);
```

#### 3. Rides Table (Core ride-hailing feature)
```sql
CREATE TABLE rides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Participants
    passenger_id UUID REFERENCES users(id) ON DELETE SET NULL,
    driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,

    -- Ride details
    ride_type VARCHAR(20) NOT NULL, -- 'moto', 'economy_car', 'comfort_car'
    status VARCHAR(20) NOT NULL DEFAULT 'requested',
    -- Status flow: 'requested' -> 'accepted' -> 'driver_arrived' -> 'in_progress' -> 'completed' / 'cancelled'

    -- Locations
    pickup_location GEOGRAPHY(POINT, 4326) NOT NULL,
    pickup_latitude DECIMAL(10, 8) NOT NULL,
    pickup_longitude DECIMAL(11, 8) NOT NULL,
    pickup_address TEXT,

    dropoff_location GEOGRAPHY(POINT, 4326) NOT NULL,
    dropoff_latitude DECIMAL(10, 8) NOT NULL,
    dropoff_longitude DECIMAL(11, 8) NOT NULL,
    dropoff_address TEXT,

    -- Fare and payment
    estimated_fare DECIMAL(10,2),
    offered_fare DECIMAL(10,2), -- Passenger's offer (InDrive style)
    counter_offer_fare DECIMAL(10,2), -- Driver's counter-offer
    final_fare DECIMAL(10,2),
    payment_method VARCHAR(20), -- 'cash', 'mtn_momo', 'orange_money'
    payment_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'refunded'
    payment_transaction_id VARCHAR(100),

    -- Distance and duration
    estimated_distance_km DECIMAL(6,2),
    estimated_duration_minutes INT,
    actual_distance_km DECIMAL(6,2),
    actual_duration_minutes INT,

    -- Ratings
    passenger_rating INT CHECK (passenger_rating BETWEEN 1 AND 5),
    driver_rating INT CHECK (driver_rating BETWEEN 1 AND 5),
    passenger_review TEXT,
    driver_review TEXT,

    -- Cancellation
    cancelled_by VARCHAR(20), -- 'passenger', 'driver', 'system'
    cancellation_reason TEXT,
    cancellation_fee DECIMAL(10,2) DEFAULT 0.00,

    -- Timestamps
    requested_at TIMESTAMP DEFAULT NOW(),
    accepted_at TIMESTAMP,
    driver_arrived_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,

    -- Metadata
    metadata JSONB, -- For additional data (route, traffic conditions, etc.)

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rides_passenger_id ON rides(passenger_id);
CREATE INDEX idx_rides_driver_id ON rides(driver_id);
CREATE INDEX idx_rides_status ON rides(status);
CREATE INDEX idx_rides_requested_at ON rides(requested_at DESC);
CREATE INDEX idx_rides_pickup_location ON rides USING GIST(pickup_location);
CREATE INDEX idx_rides_payment_status ON rides(payment_status);
```

#### 4. Ride Requests Queue (For matching algorithm)
```sql
CREATE TABLE ride_requests_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ride_id UUID UNIQUE REFERENCES rides(id) ON DELETE CASCADE,
    passenger_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Request details
    pickup_location GEOGRAPHY(POINT, 4326) NOT NULL,
    ride_type VARCHAR(20) NOT NULL,
    offered_fare DECIMAL(10,2),

    -- Matching status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'matched', 'expired', 'cancelled'
    drivers_notified UUID[], -- Array of driver IDs notified
    drivers_rejected UUID[], -- Array of driver IDs who rejected

    -- Expiry
    expires_at TIMESTAMP NOT NULL, -- Auto-expire after 5 minutes

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ride_requests_status ON ride_requests_queue(status);
CREATE INDEX idx_ride_requests_expires_at ON ride_requests_queue(expires_at);
CREATE INDEX idx_ride_requests_pickup_location ON ride_requests_queue USING GIST(pickup_location);
```

#### 5. Payments Table
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ride_id UUID REFERENCES rides(id) ON DELETE CASCADE,

    -- Payment details
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'XAF', -- Central African CFA franc
    payment_method VARCHAR(20) NOT NULL, -- 'cash', 'mtn_momo', 'orange_money'

    -- Mobile Money details
    phone_number VARCHAR(20),
    transaction_id VARCHAR(100) UNIQUE,
    external_reference VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'refunded'
    failure_reason TEXT,

    -- Commission
    platform_commission DECIMAL(10,2), -- Ehreezoh's cut (e.g., 15%)
    driver_payout DECIMAL(10,2), -- Amount driver receives

    -- Payout status
    payout_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    payout_transaction_id VARCHAR(100),
    payout_completed_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_payments_ride_id ON payments(ride_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_payout_status ON payments(payout_status);
```

#### 6. Driver Ratings Table
```sql
CREATE TABLE driver_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ride_id UUID UNIQUE REFERENCES rides(id) ON DELETE CASCADE,
    driver_id UUID REFERENCES drivers(id) ON DELETE CASCADE,
    passenger_id UUID REFERENCES users(id) ON DELETE SET NULL,

    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review TEXT,

    -- Rating categories (optional detailed feedback)
    cleanliness_rating INT CHECK (cleanliness_rating BETWEEN 1 AND 5),
    driving_rating INT CHECK (driving_rating BETWEEN 1 AND 5),
    professionalism_rating INT CHECK (professionalism_rating BETWEEN 1 AND 5),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_driver_ratings_driver_id ON driver_ratings(driver_id);
CREATE INDEX idx_driver_ratings_rating ON driver_ratings(rating);
```

#### 7. Passenger Ratings Table
```sql
CREATE TABLE passenger_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ride_id UUID UNIQUE REFERENCES rides(id) ON DELETE CASCADE,
    passenger_id UUID REFERENCES users(id) ON DELETE CASCADE,
    driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,

    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_passenger_ratings_passenger_id ON passenger_ratings(passenger_id);
```

#### 8. Incidents Table (Traffic reporting - secondary feature)
```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL, -- 'traffic_jam', 'accident', 'road_hazard'
    location GEOGRAPHY(POINT, 4326) NOT NULL, -- PostGIS geography type
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    severity INT CHECK (severity BETWEEN 1 AND 5) DEFAULT 3,
    description TEXT,
    image_url VARCHAR(500),
    reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
    verified BOOLEAN DEFAULT false,
    upvotes INT DEFAULT 0,
    downvotes INT DEFAULT 0,
    net_votes INT DEFAULT 0, -- upvotes - downvotes
    view_count INT DEFAULT 0,
    report_count INT DEFAULT 0, -- abuse reports
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'resolved', 'expired', 'flagged', 'hidden'
    metadata JSONB -- flexible field for additional data
);

-- Spatial index for fast geospatial queries
CREATE INDEX idx_incidents_location ON incidents USING GIST(location);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_created_at ON incidents(created_at DESC);
CREATE INDEX idx_incidents_expires_at ON incidents(expires_at);
CREATE INDEX idx_incidents_type ON incidents(type);
```

#### 3. Incident Votes Table
```sql
CREATE TABLE incident_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vote_type VARCHAR(10) NOT NULL, -- 'upvote' or 'downvote'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(incident_id, user_id) -- One vote per user per incident
);

CREATE INDEX idx_incident_votes_incident ON incident_votes(incident_id);
CREATE INDEX idx_incident_votes_user ON incident_votes(user_id);
```

#### 4. Incident Reports (Abuse) Table
```sql
CREATE TABLE incident_abuse_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    reporter_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reason VARCHAR(100) NOT NULL, -- 'false_info', 'spam', 'inappropriate', 'duplicate'
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_abuse_reports_incident ON incident_abuse_reports(incident_id);
```

#### 5. User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(255),
    fcm_token VARCHAR(500), -- Firebase Cloud Messaging token
    platform VARCHAR(20), -- 'ios' or 'android'
    app_version VARCHAR(20),
    last_active_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_fcm_token ON user_sessions(fcm_token);
```

### Redis Cache Structure

```
# ===== RIDE-HAILING (Primary Feature) =====

# Online drivers by location (geospatial index)
drivers:online:locations -> GEOADD with driver_id, lat, lng
TTL: 30 seconds (auto-refresh by driver app)

# Driver details cache
driver:{driver_id}:details -> JSON (status, vehicle, rating)
TTL: 5 minutes

# Driver availability status
driver:{driver_id}:available -> BOOLEAN
TTL: 1 minute

# Active ride requests queue
ride_requests:pending -> Sorted Set (score = timestamp)
TTL: 5 minutes

# Ride details cache (for active rides)
ride:{ride_id}:details -> JSON
TTL: 2 hours

# Driver's current ride
driver:{driver_id}:current_ride -> ride_id
TTL: 2 hours

# Passenger's current ride
passenger:{passenger_id}:current_ride -> ride_id
TTL: 2 hours

# Real-time driver location during ride
ride:{ride_id}:driver_location -> JSON {lat, lng, heading, speed, timestamp}
TTL: 10 seconds (updated every 3 seconds)

# Ride matching lock (prevent double-matching)
ride:{ride_id}:matching_lock -> BOOLEAN
TTL: 30 seconds

# Driver notification queue
driver:{driver_id}:notifications -> List[ride_request_id]
TTL: 5 minutes

# Payment processing lock
payment:{ride_id}:processing -> BOOLEAN
TTL: 2 minutes

# ===== TRAFFIC REPORTING (Secondary Feature) =====

# Active incidents by region (geohash)
incidents:geo:{geohash} -> List[incident_id]
TTL: 30 minutes

# Incident details
incident:{incident_id} -> JSON
TTL: 1 hour

# ===== GENERAL =====

# User rate limiting
ratelimit:ride_request:{user_id} -> count
TTL: 1 hour

ratelimit:report:{user_id} -> count
TTL: 1 hour

# WebSocket room subscriptions
ws:room:{geohash} -> Set[connection_id]
TTL: Session-based

# User session cache
session:{user_id} -> JSON
TTL: 24 hours

# FCM tokens for push notifications
user:{user_id}:fcm_tokens -> Set[token]
TTL: 30 days
```

---

## API Specification

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.ehreezoh.cm/api/v1
```

### Authentication
All protected endpoints require Firebase JWT token in header:
```
Authorization: Bearer <firebase_jwt_token>
```

### API Versioning
- Current version: v1
- Breaking changes will increment version (v2, v3, etc.)
- Deprecated endpoints supported for 6 months

---

## Endpoints

### Authentication

**POST /auth/register**
```json
Request:
{
  "firebase_uid": "string",
  "phone_number": "+237XXXXXXXXX",
  "username": "string (optional)",
  "language_preference": "fr|en"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "username": "string",
    "trust_score": 0.00,
    "created_at": "2025-11-11T10:00:00Z"
  }
}
```

**POST /auth/login**
```json
Request:
{
  "firebase_uid": "string",
  "device_id": "string",
  "fcm_token": "string",
  "platform": "ios|android",
  "user_type": "passenger|driver|both"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "user": {
      "user_id": "uuid",
      "phone_number": "+237XXXXXXXXX",
      "full_name": "string",
      "is_passenger": true,
      "is_driver": false,
      "is_verified": true
    },
    "driver_profile": {  // Only if is_driver = true
      "driver_id": "uuid",
      "vehicle_type": "moto",
      "vehicle_plate": "ABC-123",
      "is_verified": true,
      "average_rating": 4.8,
      "total_rides": 150
    },
    "session_id": "uuid"
  }
}
```

---

### Ride-Hailing (Primary Feature)

#### Passenger Endpoints

**POST /rides/request**
```json
Request:
{
  "pickup_latitude": 4.0511,
  "pickup_longitude": 9.7679,
  "pickup_address": "Akwa, Douala",
  "dropoff_latitude": 4.0611,
  "dropoff_longitude": 9.7879,
  "dropoff_address": "Bonanjo, Douala",
  "ride_type": "moto|economy_car|comfort_car",
  "offered_fare": 1500,  // Optional: passenger's offer (XAF)
  "payment_method": "cash|mtn_momo|orange_money"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "ride_id": "uuid",
    "status": "requested",
    "estimated_fare": 1200,
    "estimated_distance_km": 5.2,
    "estimated_duration_minutes": 15,
    "expires_at": "2025-11-11T10:35:00Z",  // 5 minutes
    "nearby_drivers_count": 8
  }
}
```

**GET /rides/{ride_id}**
```json
Response: 200 OK
{
  "success": true,
  "data": {
    "ride_id": "uuid",
    "status": "accepted",
    "passenger": {
      "name": "John Doe",
      "phone": "+237XXXXXXXXX",
      "rating": 4.9
    },
    "driver": {
      "driver_id": "uuid",
      "name": "Driver Name",
      "phone": "+237XXXXXXXXX",
      "photo_url": "https://...",
      "vehicle_type": "moto",
      "vehicle_plate": "ABC-123",
      "vehicle_color": "Red",
      "rating": 4.8,
      "total_rides": 150,
      "current_location": {"lat": 4.0520, "lng": 9.7690},
      "eta_minutes": 5
    },
    "pickup": {
      "latitude": 4.0511,
      "longitude": 9.7679,
      "address": "Akwa, Douala"
    },
    "dropoff": {
      "latitude": 4.0611,
      "longitude": 9.7879,
      "address": "Bonanjo, Douala"
    },
    "fare": {
      "estimated": 1200,
      "offered": 1500,
      "counter_offer": null,
      "final": 1500
    },
    "payment_method": "mtn_momo",
    "requested_at": "2025-11-11T10:30:00Z",
    "accepted_at": "2025-11-11T10:31:00Z"
  }
}
```

**PATCH /rides/{ride_id}/cancel**
```json
Request:
{
  "reason": "Changed my mind|Found another ride|Driver too far|Other",
  "details": "Optional explanation"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "ride_id": "uuid",
    "status": "cancelled",
    "cancellation_fee": 0,  // Fee if cancelled after driver accepted
    "cancelled_at": "2025-11-11T10:32:00Z"
  }
}
```

**POST /rides/{ride_id}/rate**
```json
Request:
{
  "rating": 5,
  "review": "Great driver, very professional!",
  "cleanliness_rating": 5,
  "driving_rating": 5,
  "professionalism_rating": 5
}

Response: 201 Created
{
  "success": true,
  "message": "Rating submitted successfully"
}
```

**GET /rides/history**
```
Query Parameters:
- limit: int (default: 20, max: 100)
- offset: int (default: 0)
- status: string (optional: "completed", "cancelled")

Response: 200 OK
{
  "success": true,
  "data": {
    "rides": [
      {
        "ride_id": "uuid",
        "driver_name": "Driver Name",
        "vehicle_type": "moto",
        "pickup_address": "Akwa, Douala",
        "dropoff_address": "Bonanjo, Douala",
        "fare": 1500,
        "distance_km": 5.2,
        "duration_minutes": 18,
        "status": "completed",
        "completed_at": "2025-11-11T10:50:00Z"
      }
    ],
    "meta": {
      "total": 45,
      "limit": 20,
      "offset": 0
    }
  }
}
```

#### Driver Endpoints

**POST /drivers/register**
```json
Request (multipart/form-data):
{
  "full_name": "string",
  "driver_license_number": "string",
  "driver_license_photo": "file",
  "national_id_number": "string",
  "national_id_photo": "file",
  "vehicle_type": "moto|economy_car|comfort_car",
  "vehicle_make": "Honda",
  "vehicle_model": "CBR",
  "vehicle_year": 2020,
  "vehicle_color": "Red",
  "vehicle_plate_number": "ABC-123",
  "vehicle_photo": "file"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "driver_id": "uuid",
    "verification_status": "pending",
    "message": "Application submitted. Verification typically takes 24-48 hours."
  }
}
```

**PATCH /drivers/status**
```json
Request:
{
  "is_online": true,
  "is_available": true
}

Response: 200 OK
{
  "success": true,
  "data": {
    "driver_id": "uuid",
    "is_online": true,
    "is_available": true
  }
}
```

**POST /drivers/location**
```json
Request:
{
  "latitude": 4.0511,
  "longitude": 9.7679,
  "heading": 45,  // degrees
  "speed": 30  // km/h
}

Response: 200 OK
{
  "success": true,
  "message": "Location updated"
}
```

**GET /drivers/ride-requests**
```
Response: 200 OK
{
  "success": true,
  "data": {
    "pending_requests": [
      {
        "ride_id": "uuid",
        "passenger_name": "John Doe",
        "passenger_rating": 4.9,
        "pickup_location": {"lat": 4.0511, "lng": 9.7679},
        "pickup_address": "Akwa, Douala",
        "dropoff_location": {"lat": 4.0611, "lng": 9.7879},
        "dropoff_address": "Bonanjo, Douala",
        "distance_to_pickup_km": 1.2,
        "estimated_fare": 1200,
        "offered_fare": 1500,
        "ride_type": "moto",
        "requested_at": "2025-11-11T10:30:00Z",
        "expires_at": "2025-11-11T10:35:00Z"
      }
    ]
  }
}
```

**POST /drivers/rides/{ride_id}/accept**
```json
Request:
{
  "counter_offer_fare": 1300  // Optional: driver's counter-offer
}

Response: 200 OK
{
  "success": true,
  "data": {
    "ride_id": "uuid",
    "status": "accepted",
    "final_fare": 1500,  // or counter_offer if passenger accepts
    "passenger": {
      "name": "John Doe",
      "phone": "+237XXXXXXXXX",
      "rating": 4.9
    },
    "pickup_location": {"lat": 4.0511, "lng": 9.7679}
  }
}
```

**POST /drivers/rides/{ride_id}/reject**
```json
Request:
{
  "reason": "Too far|Low fare|Other"
}

Response: 200 OK
{
  "success": true,
  "message": "Ride request rejected"
}
```

**PATCH /drivers/rides/{ride_id}/status**
```json
Request:
{
  "status": "driver_arrived|in_progress|completed"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "ride_id": "uuid",
    "status": "in_progress",
    "updated_at": "2025-11-11T10:35:00Z"
  }
}
```

**GET /drivers/earnings**
```
Query Parameters:
- period: string (today|week|month|all)
- start_date: date (optional)
- end_date: date (optional)

Response: 200 OK
{
  "success": true,
  "data": {
    "total_earnings": 45000,
    "platform_commission": 6750,  // 15%
    "net_earnings": 38250,
    "total_rides": 30,
    "completed_rides": 28,
    "cancelled_rides": 2,
    "average_fare": 1500,
    "pending_payout": 5000,
    "breakdown": [
      {
        "date": "2025-11-11",
        "rides": 5,
        "earnings": 7500,
        "commission": 1125,
        "net": 6375
      }
    ]
  }
}
```

**POST /drivers/payout**
```json
Request:
{
  "amount": 38250,
  "payment_method": "mtn_momo|orange_money",
  "phone_number": "+237XXXXXXXXX"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "payout_id": "uuid",
    "amount": 38250,
    "status": "processing",
    "estimated_completion": "2025-11-11T11:00:00Z"
  }
}
```

---

### Traffic Reporting (Secondary Feature)

#### Incidents

**POST /incidents**
```json
Request (multipart/form-data):
{
  "type": "traffic_jam|accident|road_hazard",
  "latitude": 4.0511,
  "longitude": 9.7679,
  "severity": 1-5,
  "description": "string (optional)",
  "image": "file (optional, max 5MB)"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "incident_id": "uuid",
    "type": "traffic_jam",
    "location": {"lat": 4.0511, "lng": 9.7679},
    "severity": 3,
    "expires_at": "2025-11-11T11:00:00Z",
    "created_at": "2025-11-11T10:30:00Z"
  }
}
```

**GET /incidents/nearby**
```
Query Parameters:
- latitude: float (required)
- longitude: float (required)
- radius: int (meters, default: 5000, max: 50000)
- types: comma-separated (optional, e.g., "traffic_jam,accident")
- limit: int (default: 50, max: 200)

Response: 200 OK
{
  "success": true,
  "data": {
    "incidents": [
      {
        "id": "uuid",
        "type": "traffic_jam",
        "location": {"lat": 4.0511, "lng": 9.7679},
        "severity": 3,
        "description": "Heavy traffic on Rue de la Joie",
        "image_url": "https://...",
        "upvotes": 5,
        "downvotes": 0,
        "net_votes": 5,
        "verified": false,
        "distance_meters": 1250,
        "created_at": "2025-11-11T10:00:00Z",
        "expires_at": "2025-11-11T10:30:00Z"
      }
    ],
    "meta": {
      "count": 15,
      "radius_km": 5
    }
  }
}
```

**PATCH /incidents/{incident_id}/vote**
```json
Request:
{
  "vote_type": "upvote|downvote"
}

Response: 200 OK
{
  "success": true,
  "data": {
    "incident_id": "uuid",
    "upvotes": 6,
    "downvotes": 0,
    "net_votes": 6,
    "user_vote": "upvote"
  }
}
```

**DELETE /incidents/{incident_id}**
```
Response: 204 No Content
(Only reporter can delete their own incident)
```

**POST /incidents/{incident_id}/report**
```json
Request:
{
  "reason": "false_info|spam|inappropriate|duplicate",
  "details": "string (optional)"
}

Response: 201 Created
{
  "success": true,
  "message": "Report submitted successfully"
}
```

#### User

**GET /user/profile**
```
Response: 200 OK
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "username": "string",
    "trust_score": 4.5,
    "total_reports": 25,
    "verified_reports": 20,
    "upvotes_received": 100,
    "member_since": "2025-11-11"
  }
}
```

**PATCH /user/settings**
```json
Request:
{
  "language_preference": "fr|en",
  "username": "string (optional)"
}

Response: 200 OK
```

### WebSocket Events

**Connection:**
```
ws://localhost:8000/ws/incidents?token=<firebase_jwt>
```

**Client → Server Events:**

```javascript
// Subscribe to geographic area
{
  "event": "subscribe",
  "data": {
    "bounds": {
      "north": 4.1,
      "south": 4.0,
      "east": 9.8,
      "west": 9.7
    }
  }
}

// Unsubscribe
{
  "event": "unsubscribe"
}
```

**Server → Client Events:**

```javascript
// New incident created
{
  "event": "incident_created",
  "data": {
    "incident": {...}
  }
}

// Incident updated (votes, status)
{
  "event": "incident_updated",
  "data": {
    "incident_id": "uuid",
    "changes": {
      "upvotes": 10,
      "net_votes": 8
    }
  }
}

// Incident expired/resolved
{
  "event": "incident_removed",
  "data": {
    "incident_id": "uuid",
    "reason": "expired"
  }
}
```

---

## UI/UX Design Principles

### Design Philosophy
- **Simplicity First:** 3-tap maximum to report an incident
- **Offline-First:** All core features work without internet
- **Data-Conscious:** Minimize data usage at every step
- **Bilingual:** French and English throughout
- **Accessible:** Works for users with varying literacy levels

### Color Scheme
```
Primary: #E74C3C (Red) - Urgency, traffic alerts
Secondary: #3498DB (Blue) - Trust, navigation
Success: #27AE60 (Green) - Verified, safe routes
Warning: #F39C12 (Orange) - Caution, moderate severity
Danger: #C0392B (Dark Red) - High severity incidents
Background: #FFFFFF (White) / #1C1C1E (Dark mode)
Text: #2C3E50 (Dark Gray) / #ECEFF1 (Light Gray)
```

### Incident Type Icons & Colors
- 🚗 **Traffic Jam:** Red (#E74C3C)
- 💥 **Accident:** Orange (#F39C12)
- ⚠️ **Road Hazard:** Yellow (#F1C40F)

### Key Screens

#### 1. Map View (Home Screen)
- Full-screen map with user location centered
- Incident markers clustered by proximity
- Floating action button (FAB) for quick report
- Bottom sheet with incident list
- Top bar: Search, filters, settings

#### 2. Quick Report Screen
- Large icon buttons for incident types (3 options)
- Auto-detected location with manual adjustment
- Optional: Add photo, description, severity
- Submit button (prominent)
- "Report while offline" indicator

#### 3. Incident Detail Sheet
- Photo (if available)
- Incident type, severity, time ago
- Description
- Distance from user
- Upvote/Downvote buttons
- Report abuse button
- "Get directions" button

#### 4. Profile Screen
- Username, trust score
- Statistics (reports, upvotes)
- Settings: Language, notifications, data usage
- About, privacy policy, terms

### Interaction Patterns

**Quick Report Flow:**
```
1. Tap FAB (+) button
2. Select incident type (3 large buttons)
3. Confirm location (auto-detected)
4. [Optional] Add photo/details
5. Tap "Submit" → Success toast
Total: 3 taps minimum
```

**Offline Indicator:**
- Persistent banner when offline
- "Queued for upload" badge on reports
- Auto-sync notification when online

**Data Saver Mode:**
- Toggle in settings
- Disables auto-download of images
- Text-only incident list
- Reduces map tile quality

### Accessibility Features
- Minimum touch target: 44x44 dp
- High contrast mode
- Font scaling support (up to 200%)
- Screen reader compatible
- Haptic feedback for actions

---

## Cameroon-Specific Considerations

### Language Support
**Implementation:**
- Default language based on phone settings
- Manual toggle in app (FR ⇄ EN)
- All UI strings in both languages
- Server responses include localized messages

**Translation Keys:**
```json
{
  "en": {
    "ride_types": {
      "moto": "Moto-Taxi",
      "economy_car": "Economy Car",
      "comfort_car": "Comfort Car"
    },
    "ride_status": {
      "requested": "Finding Driver...",
      "accepted": "Driver Accepted",
      "driver_arrived": "Driver Arrived",
      "in_progress": "Trip in Progress",
      "completed": "Trip Completed"
    },
    "incident_types": {
      "traffic_jam": "Traffic Jam",
      "accident": "Accident",
      "road_hazard": "Road Hazard"
    },
    "actions": {
      "request_ride": "Request Ride",
      "cancel_ride": "Cancel Ride",
      "report": "Report",
      "upvote": "Confirm",
      "downvote": "Not Accurate"
    }
  },
  "fr": {
    "ride_types": {
      "moto": "Moto-Taxi",
      "economy_car": "Voiture Économique",
      "comfort_car": "Voiture Confort"
    },
    "ride_status": {
      "requested": "Recherche de Chauffeur...",
      "accepted": "Chauffeur Accepté",
      "driver_arrived": "Chauffeur Arrivé",
      "in_progress": "Course en Cours",
      "completed": "Course Terminée"
    },
    "incident_types": {
      "traffic_jam": "Embouteillage",
      "accident": "Accident",
      "road_hazard": "Danger Routier"
    },
    "actions": {
      "request_ride": "Demander une Course",
      "cancel_ride": "Annuler la Course",
      "report": "Signaler",
      "upvote": "Confirmer",
      "downvote": "Pas Exact"
    }
  }
}
```

### Ride-Hailing Specific Considerations

#### Moto-Taxi Integration (Critical for Cameroon)
**Why Moto-Taxis:**
- Most popular form of urban transport in Cameroon
- Faster in congested traffic
- More affordable than cars
- Deeply embedded in local culture
- Estimated 50,000+ moto-taxi drivers in Douala alone

**Implementation Strategy:**
1. **Prioritize Moto-Taxis in MVP:**
   - Launch with moto-taxi support first
   - Add cars in Phase 2
   - Moto-taxis are 70% of expected ride volume

2. **Driver Onboarding:**
   - Partner with existing moto-taxi unions
   - Simplified verification (driver license + bike registration)
   - Training sessions in local languages
   - Flexible commission structure (10-15% vs Uber's 25%)

3. **Safety Features:**
   - Helmet requirement verification
   - Bike condition checks
   - Driver background checks
   - Emergency contact sharing

4. **Pricing:**
   - Base fare: 200-300 XAF
   - Per km: 100-150 XAF
   - Typical ride (5km): 700-1000 XAF
   - Competitive with street negotiation prices

#### Mobile Money Integration (Essential)
**Cameroon Payment Landscape:**
- **Cash dominance:** 80% of transactions
- **Mobile Money penetration:** ~40% of adults
- **Credit cards:** <5% (not viable for MVP)

**Supported Payment Methods:**
1. **Cash (Primary - 60% of rides expected):**
   - Driver collects at trip end
   - No transaction fees
   - Instant settlement

2. **MTN Mobile Money (30% of rides):**
   - Largest mobile money provider in Cameroon
   - API integration via MTN MoMo API
   - Transaction fee: 1-2%
   - Settlement: T+1 day

3. **Orange Money (10% of rides):**
   - Second largest provider
   - API integration via Orange Money API
   - Similar fee structure to MTN

**Payment Aggregator:**
- **Campay** or **Monetbil** for unified integration
- Single API for MTN + Orange + Express Union
- Reduces integration complexity
- 2-3% transaction fee

**Driver Payout Strategy:**
- **Instant cashout** for drivers (competitive advantage)
- Minimum payout: 5,000 XAF
- Payout to Mobile Money (free for drivers)
- Weekly auto-payout option

#### Pricing Strategy
**Fare Calculation:**
```
Base Fare + (Distance × Per-KM Rate) + (Time × Per-Minute Rate)

Moto-Taxi:
- Base: 200 XAF
- Per KM: 120 XAF
- Per Minute: 20 XAF

Economy Car:
- Base: 500 XAF
- Per KM: 200 XAF
- Per Minute: 30 XAF

Comfort Car:
- Base: 800 XAF
- Per KM: 300 XAF
- Per Minute: 50 XAF
```

**Fare Negotiation (InDrive Model):**
- Passenger sees estimated fare
- Passenger can offer different amount
- Driver can accept, reject, or counter-offer
- Builds trust and transparency
- Culturally appropriate (bargaining is common)

**Commission Structure:**
- **Ehreezoh Commission:** 12-15% (vs Uber 25%, Bolt 20%)
- **Competitive advantage** for driver recruitment
- **Transparent** - shown to drivers upfront
- **No hidden fees**

#### Driver Verification Process
**Required Documents:**
1. **National ID Card** (CNI - Carte Nationale d'Identité)
2. **Driver's License** (Permis de Conduire)
3. **Vehicle Registration** (Carte Grise)
4. **Insurance Certificate** (optional for MVP, required Phase 2)

**Verification Steps:**
1. Driver submits documents via app
2. Automated checks (OCR, duplicate detection)
3. Manual review by Ehreezoh team (24-48 hours)
4. Background check (criminal record - Phase 2)
5. In-person vehicle inspection (Phase 2)
6. Approval and activation

**Verification Challenges:**
- Many drivers lack formal documentation
- Inconsistent document formats
- Limited digital infrastructure
- Solution: Flexible verification, partner with unions

#### Regulatory Compliance
**Cameroon Transport Regulations:**
- **Ministry of Transport** oversight
- **Urban transport permits** required (Phase 2)
- **Insurance requirements** (third-party liability)
- **Tax obligations** (driver income tax, VAT)

**Legal Strategy:**
1. **Consult local lawyer** before launch
2. **Partner with transport unions** for legitimacy
3. **Engage with Ministry of Transport** early
4. **Pilot program** in one city (Douala) first
5. **Compliance-first approach** to avoid shutdown

**Potential Legal Risks:**
- Unlicensed taxi operation
- Unfair competition claims from traditional taxis
- Labor law issues (driver classification)
- Data protection compliance

**Mitigation:**
- Position as "technology platform" not transport company
- Drivers are independent contractors
- Transparent pricing and fair commissions
- Community engagement and PR

#### Local Market Dynamics
**Competition:**
- **Existing:** Uber (limited presence), Bolt (not in Cameroon yet)
- **Informal:** Street moto-taxis, traditional taxis
- **Opportunity:** Underserved market, high demand

**Competitive Advantages:**
1. **Moto-taxi focus** (competitors focus on cars)
2. **Fare negotiation** (InDrive model)
3. **Lower commissions** (12-15% vs 25%)
4. **Local language support** (French + English + Pidgin)
5. **Cash payment** (competitors push cashless)
6. **Traffic intelligence** (unique differentiator)
7. **Cameroon-first** (not international expansion)

**Target Cities (Launch Order):**
1. **Douala** (MVP launch) - Economic capital, 3M+ population
2. **Yaoundé** (Phase 2) - Political capital, 2.5M+ population
3. **Bamenda, Bafoussam, Garoua** (Phase 3)

### Network Optimization
**Strategies:**
1. **Image Compression:**
   - Client-side: Resize to max 1024px, 70% quality
   - Server-side: Generate thumbnails (200px, 400px)
   - Format: WebP (90% smaller than JPEG)

2. **API Response Compression:**
   - Gzip compression (reduces payload by 70-80%)
   - Pagination (max 50 incidents per request)
   - Field filtering (only return needed fields)

3. **Map Tile Optimization:**
   - Vector tiles (smaller than raster)
   - Cache tiles locally (50MB limit)
   - Download on WiFi prompt

4. **Offline Caching:**
   - Cache incidents for 24 hours
   - Cache map tiles for user's city
   - Queue reports when offline

**Data Usage Targets:**
- First launch: <10 MB
- Daily active use: <5 MB
- Weekly active use: <20 MB

### Cultural Adaptations
- **Community-First:** Emphasize helping fellow drivers
- **Trust Building:** Show verification badges prominently
- **Local Landmarks:** Use well-known locations in examples
- **Informal Language:** Friendly, conversational tone (not corporate)

### Legal Compliance
**Privacy Policy Requirements:**
- GDPR-inspired (even though Cameroon not in EU)
- Clear data usage explanation
- User rights: Access, delete, export data
- Consent for location tracking
- Available in French and English

**Terms of Service:**
- User-generated content disclaimer
- Prohibited activities (spam, false reports)
- Account termination conditions
- Limitation of liability
- Governing law: Cameroon

**Important Note:**
⚠️ **Police checkpoint reporting is EXCLUDED from MVP** pending legal consultation with Cameroon lawyer.

---

## Safety & Ethical Guidelines

### Privacy-First Principles

**Data Minimization:**
- Collect only essential data
- No real names required
- No email addresses
- No precise location history (only incident locations)

**Data Retention:**
- Incidents: Auto-delete after expiry + 7 days
- User location: Never stored (only incident locations)
- Photos: Delete when incident expires
- User sessions: 30 days inactive = delete

**Encryption:**
- TLS 1.3 for all communications
- Phone numbers hashed (bcrypt)
- Local database encrypted (SQLCipher)
- Images stored with random UUIDs (no metadata)

### Content Moderation

**Automated Filters:**
1. **Rate Limiting:**
   - Anonymous: 3 reports/day
   - Registered: 10 reports/day
   - Trusted users: 20 reports/day

2. **Duplicate Detection:**
   - Same type + location (100m) within 10 min = merge
   - Credit all reporters

3. **Spam Detection:**
   - Identical descriptions flagged
   - Repeated reports from same user/location
   - Suspicious patterns (always same time)

4. **Auto-Expiry:**
   - Traffic jam: 30 minutes
   - Accident: 4 hours
   - Road hazard: 24 hours

**Community Moderation:**
- Net votes < -5 → Auto-hide
- 5+ abuse reports → Flag for review
- Upvotes extend visibility

**Manual Review:**
- Flagged content reviewed within 24 hours
- Admin dashboard for moderation
- User appeal process

### User Safety

**Driver Safety:**
- Prominent "Don't use while driving" warning on launch
- "I'm a passenger" confirmation before reporting
- Voice input (Phase 2) for hands-free reporting

**Data Safety:**
- No personal information in reports
- Anonymous reporting option
- Location fuzzing (round to nearest 50m)

**Community Guidelines:**
```
✅ DO:
- Report accurate, timely information
- Help other drivers stay safe
- Verify reports when you can
- Be respectful

❌ DON'T:
- Submit false reports
- Spam the system
- Share personal information
- Use while driving
```

---

## Development Phases

### Phase 1: MVP (Weeks 1-16) - Current Phase

**Week 1-2: Setup & Planning** ✅ COMPLETE
- [x] Project documentation (comprehensive)
- [x] Technology stack confirmation
- [x] Project structure setup
- [x] Git repository initialization
- [x] Docker Compose configuration
- [x] CI/CD pipeline (GitHub Actions)
- [ ] Wireframes and mockups (passenger + driver apps)
- [ ] Firebase project setup
- [ ] Mapbox account setup
- [ ] Mobile Money API accounts (MTN, Orange, Campay)

**Week 3-5: Backend Foundation - Ride-Hailing Core**
- [ ] PostgreSQL + PostGIS setup
- [ ] Database schema implementation (users, drivers, rides, payments, ratings)
- [ ] Alembic migrations
- [ ] Firebase Auth integration
- [ ] Driver registration and verification API
- [ ] Ride request/accept/cancel endpoints
- [ ] Real-time driver location tracking (Redis geospatial)
- [ ] Driver-passenger matching algorithm
- [ ] Fare calculation engine
- [ ] Payment integration (Mobile Money APIs)
- [ ] Rating system API
- [ ] WebSocket setup for real-time tracking
- [ ] Unit tests for core business logic

**Week 6-8: Mobile Apps - Passenger & Driver**
- [ ] React Native project initialization (shared codebase)
- [ ] Role-based navigation (passenger vs driver)
- [ ] Mapbox integration
- [ ] User location tracking (foreground + background)
- [ ] **Passenger App:**
  - [ ] Request ride screen (pickup/dropoff selection)
  - [ ] Ride type selection (moto, economy, comfort)
  - [ ] Fare estimation display
  - [ ] Driver tracking screen (real-time location)
  - [ ] Trip history
  - [ ] Payment method selection
- [ ] **Driver App:**
  - [ ] Online/offline toggle
  - [ ] Incoming ride requests screen
  - [ ] Accept/reject/counter-offer UI
  - [ ] Navigation to pickup
  - [ ] Trip in progress screen
  - [ ] Earnings dashboard
- [ ] i18n setup (French/English)
- [ ] Offline storage (WatermelonDB)

**Week 9-11: Payments, Ratings & Traffic Reporting**
- [ ] Mobile Money payment integration (MTN, Orange)
- [ ] Payment UI (passenger app)
- [ ] Payout system (driver app)
- [ ] Driver rating screen (passenger)
- [ ] Passenger rating screen (driver)
- [ ] Trip receipt generation
- [ ] **Traffic Reporting (Secondary Feature):**
  - [ ] Incident reporting UI (both apps)
  - [ ] Photo upload & compression
  - [ ] Display incidents on map
  - [ ] Upvote/downvote functionality
  - [ ] Traffic-aware routing suggestions
- [ ] Push notifications (FCM)
- [ ] Emergency SOS button

**Week 12-14: Real-time Features & Testing**
- [ ] WebSocket real-time ride tracking
- [ ] Live driver location updates (every 3 seconds)
- [ ] Push notifications for ride requests
- [ ] Push notifications for ride status changes
- [ ] Real-time fare negotiation
- [ ] Trip sharing (share ETA with contacts)
- [ ] Unit tests (backend)
- [ ] Integration tests (API)
- [ ] Component tests (mobile)
- [ ] End-to-end testing (ride flow)
- [ ] Performance testing (matching algorithm)
- [ ] Load testing (concurrent rides)

**Week 15-16: Launch Preparation**
- [ ] Driver onboarding process
- [ ] Driver verification workflow (admin panel)
- [ ] Beta testing (50 passengers, 20 drivers)
- [ ] Bug fixes and optimization
- [ ] App store assets (screenshots, descriptions)
- [ ] Privacy policy and terms of service
- [ ] Regulatory compliance (Cameroon transport laws)
- [ ] Marketing materials (landing page, social media)
- [ ] Google Play Store submission
- [ ] Soft launch (Douala only)

### Phase 2: Enhanced Features (Weeks 17-28)

**Ride-Hailing Enhancements:**
- Scheduled rides / ride reservations
- Multi-stop rides
- Ride-sharing (carpooling multiple passengers)
- In-app chat between driver and passenger
- Corporate accounts for businesses
- Driver referral program
- Loyalty/rewards program for passengers
- Advanced analytics dashboard for drivers
- Heat maps for high-demand areas
- Surge pricing during peak hours

**Traffic Intelligence Enhancements:**
- User profiles and reputation system
- Comments on incidents
- Route planning with incident avoidance
- Voice reporting (hands-free)
- Community verification badges
- Traffic prediction (ML-based)

**Platform Expansion:**
- iOS version
- Delivery services (Ehreezoh Delivery)
- Food delivery integration
- Expansion to Yaoundé
- Expansion to other Cameroon cities

### Phase 3: Scale & Monetization (Week 29+)

**Business Model:**
- Premium passenger features (priority matching, ad-free)
- Driver subscription tiers (lower commission rates)
- Business API for corporate clients
- Advertising platform (in-app ads for local businesses)
- Data licensing (traffic insights to government/urban planners)

**Technology:**
- Machine learning for demand prediction
- AI-powered fraud detection
- Advanced route optimization
- Multi-language support (Pidgin, local languages)
- Regional expansion (Chad, Gabon, Congo)

**Operations:**
- Driver training programs
- Insurance partnerships
- Vehicle financing partnerships
- 24/7 customer support
- Driver support centers

---

## Deployment Strategy

### Development Environment
```
Local Development:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Mobile: Expo Go / Android Emulator
```

### Staging Environment
```
Staging Server (DigitalOcean Droplet):
- API: https://staging-api.trafficcm.app
- Database: Managed PostgreSQL
- Redis: Managed Redis
- Purpose: Beta testing, QA
```

### Production Environment
```
Production (DigitalOcean / AWS):
- API: https://api.trafficcm.app
- CDN: Cloudflare (static assets, images)
- Database: Managed PostgreSQL (with replicas)
- Redis: Managed Redis (with persistence)
- Monitoring: Sentry, Datadog
- Backups: Daily automated backups
```

### CI/CD Pipeline
```yaml
GitHub Actions Workflow:
1. On push to main:
   - Run tests (pytest, jest)
   - Lint code (flake8, eslint)
   - Build Docker image
   - Push to registry

2. On tag (v*):
   - Deploy to staging
   - Run smoke tests
   - Manual approval
   - Deploy to production

3. Mobile (on release branch):
   - Build APK/IPA
   - Upload to App Store / Play Store
   - Create GitHub release
```

### Monitoring & Alerts
- **Error Tracking:** Sentry (backend + mobile)
- **Performance:** Firebase Performance Monitoring
- **Analytics:** Firebase Analytics
- **Uptime:** UptimeRobot (API health checks)
- **Logs:** Centralized logging (Papertrail / CloudWatch)

### Backup Strategy
- **Database:** Daily automated backups (7-day retention)
- **Images:** S3 versioning enabled
- **Code:** Git (GitHub)
- **Disaster Recovery:** Restore time < 1 hour

---

## Cost Estimates

### MVP Phase (Months 1-3)
```
Infrastructure:
- DigitalOcean Droplet (2GB): $12/month
- Managed PostgreSQL: $15/month
- Managed Redis: $10/month
- Cloudflare CDN: Free
- Firebase (Auth + FCM): Free tier
- Mapbox: Free tier (50K loads)
- Domain: $12/year
Total: ~$40/month

Development (if outsourced):
- Freelance developer: $3,000-8,000 (one-time)
```

### Growth Phase (10K users)
```
- Servers: $50/month
- Database: $30/month
- Redis: $15/month
- Mapbox: $50/month
- Firebase: $25/month
- CDN: $20/month
Total: ~$190/month
```

---

## Success Metrics

### MVP Success Criteria
- 500+ downloads in first month
- 100+ active daily users
- 50+ incidents reported daily
- <5% crash rate
- 4.0+ app store rating
- <3 second average API response time

### Key Performance Indicators (KPIs)
- **User Engagement:** Daily Active Users (DAU)
- **Content Quality:** % of verified incidents
- **Retention:** 7-day and 30-day retention rates
- **Performance:** App load time, API latency
- **Reliability:** Uptime %, crash-free sessions

---

## Contact & Support

**Project Lead:** [Your Name]
**Email:** support@trafficcm.app
**GitHub:** https://github.com/[username]/cameroon-traffic-app
**Documentation:** https://docs.trafficcm.app

---

**Last Updated:** November 11, 2025
**Version:** 1.0.0 (MVP)

