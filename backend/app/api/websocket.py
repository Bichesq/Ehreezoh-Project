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
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise Exception("Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise Exception("User not found")
        
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
                ride_id = message.get("ride_id")
                if ride_id:
                    manager.join_ride_room(ride_id, user.id)
                    await websocket.send_json(create_event(
                        event_type="joined_ride",
                        data={"ride_id": ride_id}
                    ))
            
            # Handle leave ride room
            elif message_type == "leave_ride":
                ride_id = message.get("ride_id")
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
                    await websocket.send_json(create_event(
                        event_type="driver_status",
                        data={"online": True}
                    ))
            
            # Handle driver going offline
            elif message_type == "driver_offline":
                if user.is_driver:
                    manager.mark_driver_offline(user.id)
                    await websocket.send_json(create_event(
                        event_type="driver_status",
                        data={"online": False}
                    ))
            
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
