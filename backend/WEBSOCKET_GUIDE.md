# 🔌 WebSocket Real-Time Updates - Complete Guide

## Overview

WebSocket support enables real-time bidirectional communication between the server and clients (drivers and passengers).

## Connection

### WebSocket Endpoint
```
ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN
```

### Authentication
Pass JWT token as query parameter when connecting.

---

## Client Implementation Examples

### JavaScript/TypeScript
```javascript
// Connect to WebSocket
const token = "YOUR_JWT_TOKEN";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/connect?token=${token}`);

// Connection opened
ws.onopen = () => {
  console.log('✅ WebSocket connected');
  
  // Send ping to keep connection alive
  setInterval(() => {
    ws.send(JSON.stringify({ type: 'ping', timestamp: new Date().toISOString() }));
  }, 30000); // Every 30 seconds
};

// Receive messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('📨 Received:', message);
  
  switch (message.type) {
    case 'connected':
      console.log('Connected as:', message.data.user_id);
      break;
    
    case 'ride_accepted':
      console.log('Driver accepted ride:', message.data);
      // Update UI with driver info
      break;
    
    case 'driver_location_update':
      console.log('Driver location:', message.data);
      // Update map with driver location
      break;
    
    case 'ride_started':
      console.log('Ride started');
      // Navigate to in-ride screen
      break;
    
    case 'ride_completed':
      console.log('Ride completed');
      // Show rating screen
      break;
  }
};

// Join a ride room (to receive ride-specific updates)
function joinRide(rideId) {
  ws.send(JSON.stringify({
    type: 'join_ride',
    ride_id: rideId
  }));
}

// Mark driver as online
function goOnline() {
  ws.send(JSON.stringify({
    type: 'driver_online'
  }));
}
```

### Python Client
```python
import asyncio
import websockets
import json

async def connect_websocket(token):
    uri = f"ws://localhost:8000/api/v1/ws/connect?token={token}"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection confirmation
        message = await websocket.recv()
        print(f"Connected: {message}")
        
        # Join a ride room
        await websocket.send(json.dumps({
            "type": "join_ride",
            "ride_id": "ride-uuid-here"
        }))
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")

# Run
asyncio.run(connect_websocket("YOUR_JWT_TOKEN"))
```

---

## Event Types

### Connection Events

#### `connected`
Sent when WebSocket connection is established.
```json
{
  "type": "connected",
  "data": {
    "user_id": "user-uuid",
    "phone_number": "+237123456789",
    "is_driver": false
  },
  "timestamp": "2025-12-19T03:00:00Z"
}
```

---

### Ride Events

#### `ride_requested`
New ride request created (sent to nearby drivers).
```json
{
  "type": "ride_requested",
  "data": {
    "ride_id": "ride-uuid",
    "passenger_id": "user-uuid",
    "ride_type": "moto",
    "pickup_latitude": 3.8480,
    "pickup_longitude": 11.5021,
    "dropoff_latitude": 3.8580,
    "dropoff_longitude": 11.5121,
    "estimated_fare": 1500
  },
  "metadata": {
    "ride_id": "ride-uuid"
  },
  "timestamp": "2025-12-19T03:00:00Z"
}
```

#### `ride_accepted`
Driver accepted the ride.
```json
{
  "type": "ride_accepted",
  "data": {
    "ride_id": "ride-uuid",
    "driver_id": "driver-uuid",
    "driver_name": "John Doe",
    "vehicle_type": "moto",
    "vehicle_plate": "CM-1234-AB",
    "vehicle_color": "Black",
    "driver_rating": 4.8,
    "estimated_arrival": 5
  },
  "timestamp": "2025-12-19T03:01:00Z"
}
```

#### `ride_started`
Ride has started (passenger picked up).
```json
{
  "type": "ride_started",
  "data": {
    "ride_id": "ride-uuid",
    "started_at": "2025-12-19T03:05:00Z"
  },
  "timestamp": "2025-12-19T03:05:00Z"
}
```

#### `ride_completed`
Ride completed successfully.
```json
{
  "type": "ride_completed",
  "data": {
    "ride_id": "ride-uuid",
    "final_fare": 1500,
    "completed_at": "2025-12-19T03:15:00Z"
  },
  "timestamp": "2025-12-19T03:15:00Z"
}
```

#### `ride_cancelled`
Ride was cancelled.
```json
{
  "type": "ride_cancelled",
  "data": {
    "ride_id": "ride-uuid",
    "cancelled_by": "passenger",
    "reason": "Changed my mind"
  },
  "timestamp": "2025-12-19T03:02:00Z"
}
```

---

### Driver Events

#### `driver_location_update`
Driver's location changed (sent every 10-30 seconds).
```json
{
  "type": "driver_location_update",
  "data": {
    "driver_id": "driver-uuid",
    "latitude": 3.8485,
    "longitude": 11.5025,
    "heading": 45,
    "speed": 25
  },
  "timestamp": "2025-12-19T03:00:30Z"
}
```

#### `driver_arrived`
Driver arrived at pickup location.
```json
{
  "type": "driver_arrived",
  "data": {
    "ride_id": "ride-uuid",
    "driver_id": "driver-uuid"
  },
  "timestamp": "2025-12-19T03:04:00Z"
}
```

---

### Client Messages

#### Ping/Pong (Heartbeat)
```json
// Client sends
{
  "type": "ping",
  "timestamp": "2025-12-19T03:00:00Z"
}

// Server responds
{
  "type": "pong",
  "data": {
    "timestamp": "2025-12-19T03:00:00Z"
  },
  "timestamp": "2025-12-19T03:00:00Z"
}
```

#### Join Ride Room
```json
{
  "type": "join_ride",
  "ride_id": "ride-uuid"
}
```

#### Leave Ride Room
```json
{
  "type": "leave_ride",
  "ride_id": "ride-uuid"
}
```

#### Driver Online/Offline
```json
// Go online
{
  "type": "driver_online"
}

// Go offline
{
  "type": "driver_offline"
}
```

---

## Use Cases

### Passenger App

1. **Request Ride**
   - Connect to WebSocket
   - Request ride via REST API
   - Join ride room: `{"type": "join_ride", "ride_id": "..."}`
   - Listen for `ride_accepted` event
   - Listen for `driver_location_update` to show driver approaching
   - Listen for `driver_arrived` when driver reaches pickup
   - Listen for `ride_started` when ride begins
   - Listen for `ride_completed` when ride ends

2. **Track Driver**
   - Receive `driver_location_update` events every 10-30 seconds
   - Update map marker with driver's current position
   - Calculate ETA based on distance

### Driver App

1. **Go Online**
   - Connect to WebSocket
   - Send `{"type": "driver_online"}`
   - Update location via REST API every 10-30 seconds
   - Listen for `ride_requested` events for nearby rides

2. **Accept Ride**
   - Accept ride via REST API
   - Join ride room
   - Send location updates
   - Notify when arrived: `driver_arrived` event
   - Start ride via REST API → triggers `ride_started` event
   - Complete ride via REST API → triggers `ride_completed` event

---

## Connection Management

### Stats Endpoint
```
GET /api/v1/ws/stats
```

Returns:
```json
{
  "total_connections": 150,
  "online_drivers": 45,
  "active_rides": 12
}
```

---

## Best Practices

1. **Reconnection Logic**
   - Implement automatic reconnection with exponential backoff
   - Store last received message ID to resume from correct point

2. **Heartbeat**
   - Send ping every 30 seconds to keep connection alive
   - Close and reconnect if no pong received within 60 seconds

3. **Error Handling**
   - Handle connection errors gracefully
   - Show offline indicator to user
   - Queue messages when offline, send when reconnected

4. **Battery Optimization (Mobile)**
   - Reduce update frequency when app is in background
   - Use system location services efficiently
   - Close WebSocket when app is closed

---

## Testing

### Using `websocat` (CLI tool)
```bash
# Install websocat
# Windows: scoop install websocat
# Mac: brew install websocat
# Linux: cargo install websocat

# Connect
websocat "ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN"

# Send ping
{"type": "ping", "timestamp": "2025-12-19T03:00:00Z"}

# Join ride
{"type": "join_ride", "ride_id": "ride-uuid"}
```

### Using Browser Console
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({type: 'ping'}));
```

---

## Architecture

```
┌─────────────┐         WebSocket          ┌─────────────┐
│  Passenger  │◄──────────────────────────►│   Server    │
│     App     │                             │             │
└─────────────┘                             │  Connection │
                                            │   Manager   │
┌─────────────┐         WebSocket          │             │
│   Driver    │◄──────────────────────────►│   - Rooms   │
│     App     │                             │   - Events  │
└─────────────┘                             │   - Broadcast│
                                            └─────────────┘
                                                    │
                                                    ▼
                                            ┌─────────────┐
                                            │  REST API   │
                                            │  Endpoints  │
                                            └─────────────┘
```

---

**Status:** ✅ **READY FOR TESTING**

**Next Steps:**
1. Test WebSocket connection with Swagger UI or websocat
2. Integrate into PWA frontend
3. Add driver location broadcasting
4. Implement ride matching notifications
