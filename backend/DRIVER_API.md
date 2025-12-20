# 🚗 Driver Management API - Complete Reference

## ✅ Implemented Endpoints (5 total)

### 1. **POST** `/api/v1/drivers/register`
Register current user as a driver

**Request:**
```json
{
  "driver_license_number": "DL123456",
  "vehicle_type": "moto",
  "vehicle_plate_number": "CM-1234-AB",
  "vehicle_make": "Honda",
  "vehicle_model": "CB125",
  "vehicle_year": 2022,
  "vehicle_color": "Black"
}
```

**Response:**
```json
{
  "id": "driver-uuid",
  "user_id": "user-uuid",
  "vehicle_type": "moto",
  "is_verified": false,
  "verification_status": "pending",
  "average_rating": 0.0,
  "total_rides": 0
}
```

---

### 2. **GET** `/api/v1/drivers/me`
Get current driver's profile

**Headers:** `Authorization: Bearer JWT_TOKEN`

**Response:**
```json
{
  "id": "driver-uuid",
  "vehicle_type": "moto",
  "vehicle_plate_number": "CM-1234-AB",
  "is_online": false,
  "is_available": true,
  "is_verified": false,
  "average_rating": 4.5,
  "total_rides": 25,
  "completed_rides": 23
}
```

---

### 3. **PATCH** `/api/v1/drivers/status`
Update driver online/available status

**Request:**
```json
{
  "is_online": true,
  "is_available": true
}
```

**Use Cases:**
- Driver goes online: `{"is_online": true}`
- Driver goes offline: `{"is_online": false}`
- Driver busy on ride: `{"is_available": false}`
- Driver available again: `{"is_available": true}`

---

### 4. **POST** `/api/v1/drivers/location`
Update driver's current location (PostGIS)

**Request:**
```json
{
  "latitude": 3.8480,
  "longitude": 11.5021
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location updated",
  "latitude": 3.8480,
  "longitude": 11.5021,
  "updated_at": "2025-12-19T03:00:00Z"
}
```

**Usage:**
- Send every 10-30 seconds while online
- Used for nearby driver matching
- Stored as PostGIS geography point

---

### 5. **GET** `/api/v1/drivers/nearby`
Find nearby available drivers (Geospatial Search)

**Query Parameters:**
- `latitude` (required): Pickup latitude
- `longitude` (required): Pickup longitude
- `radius_km` (optional): Search radius (default: 5km, max: 50km)
- `vehicle_type` (optional): Filter by "moto" or "car"
- `limit` (optional): Max results (default: 10, max: 50)

**Example:**
```
GET /api/v1/drivers/nearby?latitude=3.8480&longitude=11.5021&radius_km=5&vehicle_type=moto&limit=10
```

**Response:**
```json
[
  {
    "driver_id": "driver-uuid",
    "user_id": "user-uuid",
    "full_name": "John Doe",
    "vehicle_type": "moto",
    "vehicle_plate_number": "CM-1234-AB",
    "vehicle_color": "Black",
    "average_rating": 4.8,
    "total_rides": 150,
    "distance_km": 1.25,
    "current_latitude": 3.8490,
    "current_longitude": 11.5030
  }
]
```

**Features:**
- ✅ PostGIS geospatial query (ST_DWithin)
- ✅ Distance calculation in kilometers
- ✅ Sorted by distance (closest first)
- ✅ Only verified, online, available drivers
- ✅ Vehicle type filtering

---

## 🧪 Testing Flow

### Step 1: Register as Driver
```bash
# First, login to get JWT token
POST /api/v1/auth/login
{
  "firebase_token": "..."
}

# Then register as driver
POST /api/v1/drivers/register
Authorization: Bearer YOUR_JWT_TOKEN
{
  "driver_license_number": "DL123456",
  "vehicle_type": "moto",
  "vehicle_plate_number": "CM-1234-AB"
}
```

### Step 2: Go Online
```bash
PATCH /api/v1/drivers/status
{
  "is_online": true,
  "is_available": true
}
```

### Step 3: Update Location
```bash
POST /api/v1/drivers/location
{
  "latitude": 3.8480,
  "longitude": 11.5021
}
```

### Step 4: Find Nearby Drivers (as passenger)
```bash
GET /api/v1/drivers/nearby?latitude=3.8480&longitude=11.5021&radius_km=5&vehicle_type=moto
```

---

## 🔐 Authentication

All endpoints require JWT authentication except `/nearby` (which still requires auth but can be called by passengers).

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 🎯 Key Features

### Geospatial Search
- Uses PostGIS ST_DWithin for efficient radius search
- ST_Distance for accurate distance calculation
- Geography type with SRID 4326 (WGS84)

### Driver Status Management
- `is_online`: Driver app is active
- `is_available`: Driver can accept new rides
- `is_verified`: Admin approved driver

### Real-time Location
- Location updates every 10-30 seconds
- Stored as PostGIS geography point
- Used for matching algorithm

---

## 📊 Database Schema

**drivers table:**
- `id` - UUID primary key
- `user_id` - Foreign key to users
- `driver_license_number` - Unique
- `vehicle_type` - "moto" or "car"
- `vehicle_plate_number` - Unique
- `current_location` - PostGIS Geography(POINT)
- `is_online` - Boolean
- `is_available` - Boolean
- `is_verified` - Boolean
- `average_rating` - Decimal(3,2)
- `total_rides` - Integer
- `completed_rides` - Integer

---

## ✨ Next Enhancements (Optional)

1. **Driver Verification Workflow**
   - Admin approval endpoint
   - Document upload
   - Background checks

2. **Driver Ratings**
   - Already in database
   - Need rating submission endpoint

3. **Driver Analytics**
   - Earnings dashboard
   - Performance metrics
   - Ride history

4. **Advanced Matching**
   - Driver preferences
   - Passenger ratings
   - Acceptance rate

---

**Status:** ✅ **COMPLETE AND READY FOR TESTING**

Test at: http://localhost:8000/api/docs
