"""
User profile API for mini profiles
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.incident import Incident
from app.models.gamification import Badge, UserBadge
from app.models.social import IncidentThanks, IncidentComment, UserFollow

router = APIRouter(prefix="/profiles", tags=["Profiles"])


def get_trust_level(trust_score: int) -> dict:
    """Get trust level info based on score."""
    if trust_score >= 500:
        return {"name": "Legend", "color": "#FFD700", "icon": "🌟"}
    elif trust_score >= 200:
        return {"name": "Elder", "color": "#9333ea", "icon": "👑"}
    elif trust_score >= 100:
        return {"name": "Guardian", "color": "#3b82f6", "icon": "🛡️"}
    elif trust_score >= 50:
        return {"name": "Trusted", "color": "#22c55e", "icon": "✓"}
    elif trust_score >= 10:
        return {"name": "Member", "color": "#6b7280", "icon": "👤"}
    else:
        return {"name": "Newcomer", "color": "#9ca3af", "icon": "🌱"}


@router.get("/{user_id}")
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get mini profile for a user."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get badges
    user_badges = db.query(UserBadge, Badge).join(Badge).filter(
        UserBadge.user_id == user_id
    ).order_by(desc(Badge.tier)).limit(5).all()
    
    badges = [
        {
            "name": badge.name,
            "icon": badge.icon,
            "tier": badge.tier
        }
        for ub, badge in user_badges
    ]
    
    # Stats
    incidents_reported = db.query(func.count(Incident.id)).filter(
        Incident.reporter_id == user_id
    ).scalar() or 0
    
    thanks_received = db.query(func.count(IncidentThanks.id)).filter(
        IncidentThanks.reporter_id == user_id
    ).scalar() or 0
    
    comments_made = db.query(func.count(IncidentComment.id)).filter(
        IncidentComment.user_id == user_id
    ).scalar() or 0
    
    # Follow info
    followers_count = db.query(func.count(UserFollow.id)).filter(
        UserFollow.followed_id == user_id
    ).scalar() or 0
    
    following_count = db.query(func.count(UserFollow.id)).filter(
        UserFollow.follower_id == user_id
    ).scalar() or 0
    
    is_following = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.followed_id == user_id
    ).first() is not None
    
    is_self = user_id == current_user.id
    
    trust_score = user.trust_score or 0
    trust_level = get_trust_level(trust_score)
    
    return {
        "id": user.id,
        "name": user.full_name or "Anonymous",
        "profile_photo_url": user.profile_photo_url,
        "trust_score": trust_score,
        "trust_level": trust_level,
        "badges": badges,
        "stats": {
            "incidents_reported": incidents_reported,
            "thanks_received": thanks_received,
            "comments_made": comments_made,
            "people_helped": user.total_people_helped or 0
        },
        "social": {
            "followers": followers_count,
            "following": following_count,
            "is_following": is_following
        },
        "is_self": is_self,
        "member_since": user.created_at.isoformat() if user.created_at else None
    }
