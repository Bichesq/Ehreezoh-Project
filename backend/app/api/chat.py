"""
Chat API endpoints for Neighborhood Chat
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatRoom, ChatMessage, ChatRoomMember
from app.models.community import Neighborhood, UserNeighborhood

router = APIRouter(prefix="/chat", tags=["Chat"])


# ============== SCHEMAS ==============

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    message_type: str = 'text'
    reference_id: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    room_id: str
    content: str
    message_type: str
    created_at: datetime
    user: dict
    is_pinned: bool = False

    class Config:
        orm_mode = True


# ============== ROOM ENDPOINTS ==============

@router.get("/rooms")
async def get_my_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get chat rooms for neighborhoods the user has joined."""
    
    # Get user's neighborhoods
    memberships = db.query(UserNeighborhood).filter(
        UserNeighborhood.user_id == current_user.id
    ).all()
    
    rooms = []
    for m in memberships:
        # Get or create room for this neighborhood
        room = db.query(ChatRoom).filter(
            ChatRoom.neighborhood_id == m.neighborhood_id
        ).first()
        
        if not room:
            # Create room for this neighborhood
            neighborhood = db.query(Neighborhood).filter(
                Neighborhood.id == m.neighborhood_id
            ).first()
            if neighborhood:
                room = ChatRoom(
                    neighborhood_id=neighborhood.id,
                    name=f"{neighborhood.name} Chat",
                    description=f"Community chat for {neighborhood.name}"
                )
                db.add(room)
                db.commit()
                db.refresh(room)
        
        if room:
            # Get unread count
            member = db.query(ChatRoomMember).filter(
                ChatRoomMember.room_id == room.id,
                ChatRoomMember.user_id == current_user.id
            ).first()
            
            if not member:
                # Auto-join the room
                member = ChatRoomMember(
                    room_id=room.id,
                    user_id=current_user.id
                )
                db.add(member)
                db.commit()
            
            # Count unread messages
            unread = 0
            if member.last_read_at:
                unread = db.query(func.count(ChatMessage.id)).filter(
                    ChatMessage.room_id == room.id,
                    ChatMessage.created_at > member.last_read_at,
                    ChatMessage.is_deleted == False
                ).scalar() or 0
            
            # Get last message
            last_msg = db.query(ChatMessage).filter(
                ChatMessage.room_id == room.id,
                ChatMessage.is_deleted == False
            ).order_by(desc(ChatMessage.created_at)).first()
            
            rooms.append({
                "id": room.id,
                "name": room.name,
                "neighborhood_id": room.neighborhood_id,
                "unread_count": unread,
                "last_message": {
                    "content": last_msg.content[:50] + "..." if last_msg and len(last_msg.content) > 50 else (last_msg.content if last_msg else None),
                    "created_at": last_msg.created_at.isoformat() if last_msg else None
                } if last_msg else None,
                "member_count": db.query(func.count(ChatRoomMember.id)).filter(
                    ChatRoomMember.room_id == room.id
                ).scalar() or 0
            })
    
    return rooms


@router.get("/rooms/{room_id}")
async def get_room_details(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get details of a specific chat room."""
    
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check membership
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    
    neighborhood = db.query(Neighborhood).filter(
        Neighborhood.id == room.neighborhood_id
    ).first()
    
    return {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "neighborhood": {
            "id": neighborhood.id,
            "name": neighborhood.name
        } if neighborhood else None,
        "member_count": db.query(func.count(ChatRoomMember.id)).filter(
            ChatRoomMember.room_id == room_id
        ).scalar() or 0,
        "my_role": member.role,
        "is_muted": member.is_muted
    }


# ============== MESSAGE ENDPOINTS ==============

@router.get("/rooms/{room_id}/messages")
async def get_messages(
    room_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get messages from a chat room."""
    
    # Check membership
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    
    # Query messages
    query = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id,
        ChatMessage.is_deleted == False
    )
    
    if before:
        # Pagination: get messages before this message
        before_msg = db.query(ChatMessage).filter(ChatMessage.id == before).first()
        if before_msg:
            query = query.filter(ChatMessage.created_at < before_msg.created_at)
    
    messages = query.order_by(desc(ChatMessage.created_at)).limit(limit).all()
    
    # Mark as read
    member.last_read_at = datetime.utcnow()
    db.commit()
    
    result = []
    for msg in reversed(messages):  # Reverse to get chronological order
        user = db.query(User).filter(User.id == msg.user_id).first()
        result.append({
            "id": msg.id,
            "room_id": msg.room_id,
            "content": msg.content,
            "message_type": msg.message_type,
            "reference_id": msg.reference_id,
            "is_pinned": msg.is_pinned,
            "created_at": msg.created_at.isoformat(),
            "user": {
                "id": user.id if user else None,
                "name": user.full_name if user else "Unknown",
                "profile_photo_url": user.profile_photo_url if user else None,
                "trust_score": user.trust_score if user else 0
            },
            "is_own": msg.user_id == current_user.id
        })
    
    return result


@router.post("/rooms/{room_id}/messages")
async def send_message(
    room_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Send a message to a chat room."""
    
    # Check membership
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    
    if member.is_muted:
        raise HTTPException(status_code=403, detail="You are muted in this room")
    
    # Create message
    new_message = ChatMessage(
        room_id=room_id,
        user_id=current_user.id,
        content=message.content,
        message_type=message.message_type,
        reference_id=message.reference_id
    )
    db.add(new_message)
    
    # Update last read
    member.last_read_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    # Broadcast to WebSocket
    from app.core.websocket import manager, create_event
    await manager.broadcast_to_chat_room(
        room_id,
        create_event(
            event_type="new_message",
            data={
                "id": new_message.id,
                "room_id": new_message.room_id,
                "content": new_message.content,
                "message_type": new_message.message_type,
                "created_at": new_message.created_at.isoformat(),
                "user": {
                    "id": current_user.id,
                    "name": current_user.full_name,
                    "profile_photo_url": current_user.profile_photo_url,
                    "trust_score": current_user.trust_score or 0
                },
                "is_own": False # Recipient sees it as not own
            }
        ),
        exclude_user_id=current_user.id # Sender gets response directly from HTTP
    )
    
    return {
        "id": new_message.id,
        "room_id": new_message.room_id,
        "content": new_message.content,
        "message_type": new_message.message_type,
        "created_at": new_message.created_at.isoformat(),
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "profile_photo_url": current_user.profile_photo_url,
            "trust_score": current_user.trust_score or 0
        },
        "is_own": True
    }


# ============== MODERATION ==============

@router.post("/rooms/{room_id}/messages/{message_id}/pin")
async def pin_message(
    room_id: str,
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Pin a message (moderator only)."""
    
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    if not member or member.role not in ['moderator', 'admin']:
        raise HTTPException(status_code=403, detail="Only moderators can pin messages")
    
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.room_id == room_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_pinned = not message.is_pinned
    db.commit()
    
    return {"success": True, "is_pinned": message.is_pinned}


@router.delete("/rooms/{room_id}/messages/{message_id}")
async def delete_message(
    room_id: str,
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Delete a message (own message or moderator)."""
    
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.room_id == room_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Check permissions
    is_own = message.user_id == current_user.id
    member = db.query(ChatRoomMember).filter(
        ChatRoomMember.room_id == room_id,
        ChatRoomMember.user_id == current_user.id
    ).first()
    
    is_mod = member and member.role in ['moderator', 'admin']
    
    if not is_own and not is_mod:
        raise HTTPException(status_code=403, detail="Cannot delete this message")
    
    message.is_deleted = True
    db.commit()
    
    return {"success": True, "message": "Message deleted"}
