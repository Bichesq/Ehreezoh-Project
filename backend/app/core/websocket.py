"""
Ehreezoh - WebSocket Manager
Real-time connection management and event broadcasting
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import json
import logging
from datetime import datetime
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    
    Supports:
    - User-specific connections (by user_id)
    - Ride-specific rooms (for driver-passenger communication)
    - Broadcast to all connected clients
    """
    
    def __init__(self):
        # Active connections: {user_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Ride rooms: {ride_id: Set[user_id]}
        self.ride_rooms: Dict[str, Set[str]] = {}

        # Chat rooms: {room_id: Set[user_id]}
        self.chat_rooms: Dict[str, Set[str]] = {}
        
        # Driver connections for location tracking
        self.online_drivers: Set[str] = set()
        
        # Geofenced rooms: {geohash: Set[user_id]}
        self.geo_rooms: Dict[str, Set[str]] = {}
        
        # User current geohash: {user_id: geohash}
        self.user_geohash: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        user_id = str(user_id)
        self.active_connections[user_id] = websocket
        logger.info(f"🔌 WebSocket connected: {user_id} (Total: {len(self.active_connections)})")
    
    def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"🔌 WebSocket disconnected: {user_id} (Total: {len(self.active_connections)})")
        
        # Remove from online drivers
        if user_id in self.online_drivers:
            self.online_drivers.remove(user_id)
        
        # Remove from all ride rooms
        for ride_id in list(self.ride_rooms.keys()):
            if user_id in self.ride_rooms[ride_id]:
                self.ride_rooms[ride_id].remove(user_id)
                if not self.ride_rooms[ride_id]:
                    del self.ride_rooms[ride_id]

        # Remove from all chat rooms
        for room_id in list(self.chat_rooms.keys()):
            if user_id in self.chat_rooms[room_id]:
                self.chat_rooms[room_id].remove(user_id)
                if not self.chat_rooms[room_id]:
                    del self.chat_rooms[room_id]
                    
        # Remove from geo rooms
        if user_id in self.user_geohash:
            old_geohash = self.user_geohash[user_id]
            if old_geohash in self.geo_rooms and user_id in self.geo_rooms[old_geohash]:
                self.geo_rooms[old_geohash].remove(user_id)
                if not self.geo_rooms[old_geohash]:
                    del self.geo_rooms[old_geohash]
            del self.user_geohash[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to a specific user"""
        from app.core.debug import debug_log
        user_id = str(user_id) # Ensure string
        if user_id in self.active_connections:
            # debug_log(f"WS: Sending to {user_id}")
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"❌ Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
        else:
            pass # User disconnected
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error broadcasting to {user_id}: {e}")
                disconnected.append(user_id)
        
        # Clean up disconnected clients
        for user_id in disconnected:
            self.disconnect(user_id)
    
    def join_ride_room(self, ride_id: str, user_id: str):
        """Add user to a ride-specific room"""
        if ride_id not in self.ride_rooms:
            self.ride_rooms[ride_id] = set()
        self.ride_rooms[ride_id].add(user_id)
        logger.info(f"👥 User {user_id} joined ride room {ride_id}")
    
    def leave_ride_room(self, ride_id: str, user_id: str):
        """Remove user from a ride-specific room"""
        if ride_id in self.ride_rooms and user_id in self.ride_rooms[ride_id]:
            self.ride_rooms[ride_id].remove(user_id)
            if not self.ride_rooms[ride_id]:
                del self.ride_rooms[ride_id]
            logger.info(f"👥 User {user_id} left ride room {ride_id}")

    def join_chat_room(self, room_id: str, user_id: str):
        """Add user to a chat room"""
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = set()
        self.chat_rooms[room_id].add(user_id)
        # logger.info(f"💬 User {user_id} joined chat room {room_id}")

    def leave_chat_room(self, room_id: str, user_id: str):
        """Remove user from a chat room"""
        if room_id in self.chat_rooms and user_id in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].remove(user_id)
            if not self.chat_rooms[room_id]:
                del self.chat_rooms[room_id]
            # logger.info(f"💬 User {user_id} left chat room {room_id}")
            
    async def broadcast_to_chat_room(self, room_id: str, message: dict, exclude_user_id: str = None):
        """Broadcast message to all users in a chat room"""
        if room_id in self.chat_rooms:
            for user_id in list(self.chat_rooms[room_id]):
                if exclude_user_id and user_id == exclude_user_id:
                    continue
                await self.send_personal_message(message, user_id)

    def update_geohash_subscription(self, user_id: str, geohash: str):
        """
        Update a user's subscription to a geohash room.
        Automatically removes them from the old room.
        """
        # Remove from old room if exists
        if user_id in self.user_geohash:
            old_hash = self.user_geohash[user_id]
            if old_hash == geohash:
                return # No change
                
            if old_hash in self.geo_rooms and user_id in self.geo_rooms[old_hash]:
                self.geo_rooms[old_hash].remove(user_id)
                if not self.geo_rooms[old_hash]:
                    del self.geo_rooms[old_hash]
        
        # Add to new room
        if geohash not in self.geo_rooms:
            self.geo_rooms[geohash] = set()
        self.geo_rooms[geohash].add(user_id)
        self.user_geohash[user_id] = geohash
        # logger.info(f"📍 User {user_id} subscribed to geohash {geohash}")

    async def broadcast_to_geohash(self, geohash: str, message: dict):
        """Broadcast message to all users in a specific geohash room"""
        if geohash in self.geo_rooms:
            for user_id in list(self.geo_rooms[geohash]):
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_area(self, center_geohash: str, message: dict, include_neighbors: bool = True):
        """
        Broadcast to a geohash and optionally its 8 neighbors.
        Requires pygeohash installed.
        """
        try:
            target_hashes = [center_geohash]
            if include_neighbors:
                 import pygeohash as pgh
                 neighbors = pgh.neighbors(center_geohash)
                 # neighbors returns {n, s, e, w, ne, nw, se, sw} dict values usually, but pygeohash might return list or dict?
                 # pgh.neighbors(hash) returns dictionary like {'n': '...', 's': '...'} in some libs, or list?
                 # Let's check typical usage. usually it returns a dict.
                 if isinstance(neighbors, dict):
                     target_hashes.extend(neighbors.values())
                 elif isinstance(neighbors, list):
                     target_hashes.extend(neighbors)

            unique_users = set()
            for gh in target_hashes:
                if gh in self.geo_rooms:
                    unique_users.update(self.geo_rooms[gh])
            
            for user_id in unique_users:
                 await self.send_personal_message(message, user_id)
                 
        except ImportError:
            logger.error("pygeohash not installed, broadcasting to single cell only")
            await self.broadcast_to_geohash(center_geohash, message)
    
    async def broadcast_to_ride(self, ride_id: str, message: dict):
        """Broadcast message to all users in a ride room"""
        if ride_id in self.ride_rooms:
            # Iterate over a COPY of the set, because send_personal_message -> disconnect might modify the set
            for user_id in list(self.ride_rooms[ride_id]):
                await self.send_personal_message(message, user_id)
            logger.info(f"📢 Broadcast to ride {ride_id}: {message.get('type')}")
    
    def mark_driver_online(self, user_id: str):
        """Mark driver as online for location tracking"""
        self.online_drivers.add(user_id)
    
    def mark_driver_offline(self, user_id: str):
        """Mark driver as offline"""
        if user_id in self.online_drivers:
            self.online_drivers.remove(user_id)
            redis_service.remove_driver_location(user_id)
 
    def update_driver_location(self, user_id: str, latitude: float, longitude: float):
        """Update driver's location in Redis"""
        # Implicitly mark as online if sending updates
        self.online_drivers.add(user_id)
        redis_service.update_driver_location(user_id, latitude, longitude)
    
    def get_connection_stats(self) -> dict:
        """Get current connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "online_drivers": len(self.online_drivers),
            "active_rides": len(self.ride_rooms),
            "tracked_users": len(self.user_geohash)
        }


# Global connection manager instance
manager = ConnectionManager()


# Event types for WebSocket messages
class EventType:
    """WebSocket event type constants"""
    
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    
    # Ride events
    RIDE_REQUESTED = "ride_requested"
    RIDE_ACCEPTED = "ride_accepted"
    RIDE_STARTED = "ride_started"
    RIDE_COMPLETED = "ride_completed"
    RIDE_CANCELLED = "ride_cancelled"
    
    # Payment events
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_FAILED = "payment_failed"
    
    # Matching events
    NEW_RIDE_OFFER = "new_ride_offer"
    
    # Driver events
    DRIVER_LOCATION_UPDATE = "driver_location_update"
    DRIVER_ARRIVED = "driver_arrived"
    DRIVER_NEARBY = "driver_nearby"
    
    # Passenger events
    PASSENGER_LOCATION_UPDATE = "passenger_location_update"
    
    # System events
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


def create_event(event_type: str, data: dict, metadata: Optional[dict] = None) -> dict:
    """
    Create a standardized WebSocket event message
    
    Args:
        event_type: Type of event (use EventType constants)
        data: Event payload data
        metadata: Optional metadata (user_id, ride_id, etc.)
    
    Returns:
        Formatted event dictionary
    """
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if metadata:
        event["metadata"] = metadata
    
    return event


async def broadcast_ride_update(ride_id: str, event_type: str, ride_data: dict):
    """
    Broadcast ride update to all participants
    
    Args:
        ride_id: Ride ID
        event_type: Type of update (use EventType constants)
        ride_data: Ride information
    """
    event = create_event(
        event_type=event_type,
        data=ride_data,
        metadata={"ride_id": ride_id}
    )
    
    await manager.broadcast_to_ride(ride_id, event)


async def notify_driver(driver_user_id: str, event_type: str, data: dict):
    """
    Send notification to a specific driver
    
    Args:
        driver_user_id: Driver's user ID
        event_type: Type of notification
        data: Notification data
    """
    event = create_event(event_type=event_type, data=data)
    await manager.send_personal_message(event, driver_user_id)


async def notify_passenger(passenger_user_id: str, event_type: str, data: dict):
    """
    Send notification to a specific passenger
    
    Args:
        passenger_user_id: Passenger's user ID
        event_type: Type of notification
        data: Notification data
    """
    event = create_event(event_type=event_type, data=data)
    await manager.send_personal_message(event, passenger_user_id)
