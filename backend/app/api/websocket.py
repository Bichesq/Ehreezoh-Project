"""
Ehreezoh - WebSocket API
Real-time communication endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import json
import logging

from app.core.database import get_db
from app.core.websocket import manager, EventType, create_event
from app.core.auth import decode_access_token
from app.models.user import User
from app.models.driver import Driver

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


async def get_user_from_token(token: str, db: Session) -> User:
    """
    Authenticate user from JWT token for WebSocket connection
    
    Args:
        token: JWT token
        db: Database session
    
    Returns:
        Authenticated user
    
    Raises:
        Exception: If authentication fails
    """
    try:
        logger.info(f"WS Auth: Validating token: {token[:20]}...")
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            logger.error("WS Auth: No user_id in token payload")
            raise Exception("Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"WS Auth: User {user_id} not found in DB")
            raise Exception("User not found")
            
        logger.info(f"WS Auth: Success for user {user.id}")
        return user
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        raise


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket connection endpoint for real-time updates
    
    **Authentication:**
    - Pass JWT token as query parameter: `/ws/connect?token=YOUR_JWT_TOKEN`
    
    **Message Format:**
    ```json
    {
      "type": "event_type",
      "data": {...},
      "timestamp": "2025-12-19T03:00:00Z"
    }
    ```
    
    **Event Types:**
    - `connected` - Connection established
    - `ride_requested` - New ride request
    - `ride_accepted` - Driver accepted ride
    - `ride_started` - Ride started
    - `ride_completed` - Ride completed
    - `ride_cancelled` - Ride cancelled
    - `driver_location_update` - Driver location changed
    - `ping` - Heartbeat check
    
    **Client Messages:**
    - `{"type": "ping"}` - Keep connection alive
    - `{"type": "join_ride", "ride_id": "..."}` - Join ride room
    - `{"type": "leave_ride", "ride_id": "..."}` - Leave ride room
    """
    user = None
    
    try:
        # Authenticate user
        user = await get_user_from_token(token, db)
        
        # Accept connection
        await manager.connect(websocket, user.id)
        
        # Send connection confirmation
        await websocket.send_json(create_event(
            event_type=EventType.CONNECTED,
            data={
                "user_id": user.id,
                "phone_number": user.phone_number,
                "is_driver": user.is_driver
            }
        ))
        
        # Message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            # Handle ping/pong
            if message_type == EventType.PING:
                await websocket.send_json(create_event(
                    event_type=EventType.PONG,
                    data={"timestamp": message.get("timestamp")}
                ))
            
            # Handle join ride room
            elif message_type == "join_ride":
                ride_id = message.get("ride_id") or (message.get("data") and message.get("data").get("ride_id"))
                if ride_id:
                    manager.join_ride_room(ride_id, user.id)
                    await websocket.send_json(create_event(
                        event_type="joined_ride",
                        data={"ride_id": ride_id}
                    ))
            
            # Handle leave ride room
            elif message_type == "leave_ride":
                ride_id = message.get("ride_id") or (message.get("data") and message.get("data").get("ride_id"))
                if ride_id:
                    manager.leave_ride_room(ride_id, user.id)
                    await websocket.send_json(create_event(
                        event_type="left_ride",
                        data={"ride_id": ride_id}
                    ))
            
            # Handle driver going online
            elif message_type == "driver_online":
                if user.is_driver:
                    manager.mark_driver_online(user.id)
                    
                    # Update DB
                    driver = db.query(Driver).filter(Driver.user_id == user.id).first()
                    if driver:
                        driver.is_online = True
                        db.commit()
                    
                    await websocket.send_json(create_event(
                        event_type="driver_status",
                        data={"online": True}
                    ))
            
            # Handle driver location update
            elif message_type == "driver_location_update":
                from app.core.debug import debug_log
                data = message.get("data")
                
                debug_log(f"WS: Location Update. User: {user.id}, IsDriver: {user.is_driver}, Data: {data}")
                
                if data and user.is_driver:
                    latitude = data.get("latitude")
                    longitude = data.get("longitude")
                    if latitude is not None and longitude is not None:
                        # 1. Update Redis
                        manager.update_driver_location(user.id, float(latitude), float(longitude))
                        
                        # 2. Check if driver is in an active ride
                        from app.services.redis_service import redis_service
                        current_ride_id = redis_service.get_driver_current_ride(user.id)
                        
                        if current_ride_id:
                            # 3. Broadcast to ride participants (Passenger)
                            await manager.broadcast_to_ride(
                                ride_id=current_ride_id,
                                message=create_event(
                                    event_type=EventType.DRIVER_LOCATION_UPDATE,
                                    data={
                                        "latitude": float(latitude),
                                        "longitude": float(longitude),
                                        "ride_id": current_ride_id
                                    }
                                )
                            )
                            # debug_log(f"WS: Forwarded location to ride {current_ride_id}")
                    else:
                        debug_log("WS: Lat/Lng missing")
                else:
                    debug_log("WS: Not a driver or no data")

            # Handle driver leaving offline (existing code)
            elif message_type == "driver_offline":
                if user.is_driver:
                    manager.mark_driver_offline(user.id)
                    
                    # Update DB
                    driver = db.query(Driver).filter(Driver.user_id == user.id).first()
                    if driver:
                        driver.is_online = False
                        db.commit()

                    await websocket.send_json(create_event(
                        event_type="driver_status",
                        data={"online": False}
                    ))

            # Handle Geohash Subscription for Incidents
            elif message_type == "subscribe_geohash":
                data = message.get("data")
                if data and "latitude" in data and "longitude" in data:
                    try:
                        import pygeohash as pgh
                        lat = float(data["latitude"])
                        lon = float(data["longitude"])
                        # Precision 6 is approx 1.2km x 0.6km. Good for local alerts.
                        gh = pgh.encode(lat, lon, precision=6) 
                        
                        manager.update_geohash_subscription(user.id, gh)
                    except Exception as e:
                        logger.error(f"Geohash error: {e}")
            
            # --- CHAT HANDLERS ---
            elif message_type == "join_chat":
                room_id = message.get("room_id") or (message.get("data") and message.get("data").get("room_id"))
                if room_id:
                    manager.join_chat_room(room_id, user.id)
            
            elif message_type == "leave_chat":
                room_id = message.get("room_id") or (message.get("data") and message.get("data").get("room_id"))
                if room_id:
                    manager.leave_chat_room(room_id, user.id)
                    
            elif message_type == "typing":
                data = message.get("data") or {}
                room_id = data.get("room_id")
                is_typing = data.get("is_typing", False)
                if room_id:
                    await manager.broadcast_to_chat_room(
                        room_id,
                        create_event(
                            event_type="typing", 
                            data={"user_id": user.id, "room_id": room_id, "is_typing": is_typing, "user_name": user.full_name}
                        ),
                        exclude_user_id=user.id
                    )

            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        if user:
            manager.disconnect(user.id)
            logger.info(f"WebSocket disconnected: {user.id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if user:
            manager.disconnect(user.id)
            try:
                await websocket.send_json(create_event(
                    event_type=EventType.ERROR,
                    data={"message": str(e)}
                ))
            except:
                pass
        else:
            # Connection not accepted yet (auth failed)
            try:
                await websocket.close(code=1008)
            except:
                pass


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics
    
    **Returns:**
    - Total active connections
    - Online drivers
    - Active ride rooms
    """
    return manager.get_connection_stats()


@router.get("/debug/rooms")
async def get_room_details():
    """Debug endpoint to see active rooms and their members"""
    return {
        "active_users": list(manager.active_connections.keys()),
        "ride_rooms": {k: list(v) for k, v in manager.ride_rooms.items()}
    }
