"""
Social API endpoints - Thanks and Comments
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
from app.models.incident import Incident
from app.models.social import IncidentThanks, IncidentComment, CommentUpvote, UserFollow
from app.services.gamification import gamification_service

router = APIRouter(prefix="/social", tags=["Social"])


# ============== SCHEMAS ==============

class ThanksRequest(BaseModel):
    incident_id: str

class ThanksResponse(BaseModel):
    success: bool
    message: str
    total_thanks: int

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)

class CommentResponse(BaseModel):
    id: str
    incident_id: str
    content: str
    upvotes: int
    created_at: datetime
    user: dict
    has_upvoted: bool = False

    class Config:
        orm_mode = True


# ============== THANKS ENDPOINTS ==============

@router.post("/thanks")
async def say_thanks(
    request: ThanksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ThanksResponse:
    """
    Say thank you to an incident reporter.
    Awards points to the reporter.
    """
    
    # Get incident
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if not incident.user_id:
        raise HTTPException(status_code=400, detail="Cannot thank an anonymous report")
    
    if incident.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot thank your own report")
    
    # Check if already thanked
    existing = db.query(IncidentThanks).filter(
        IncidentThanks.incident_id == request.incident_id,
        IncidentThanks.thanker_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already thanked this report")
    
    # Create thanks
    thanks = IncidentThanks(
        incident_id=request.incident_id,
        reporter_id=incident.user_id,
        thanker_id=current_user.id
    )
    db.add(thanks)
    
    # Award points to reporter
    reporter = db.query(User).filter(User.id == incident.user_id).first()
    if reporter:
        reporter.total_people_helped = (reporter.total_people_helped or 0) + 1
        gamification_service.award_points(db, reporter.id, 2, "received_thanks")
    
    db.commit()
    
    # Count total thanks for this incident
    total = db.query(func.count(IncidentThanks.id)).filter(
        IncidentThanks.incident_id == request.incident_id
    ).scalar() or 0
    
    return ThanksResponse(
        success=True,
        message="Thanks sent! Reporter has been notified.",
        total_thanks=total
    )


@router.get("/thanks/{incident_id}")
async def get_thanks_count(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get thanks count for an incident and check if user has thanked."""
    
    total = db.query(func.count(IncidentThanks.id)).filter(
        IncidentThanks.incident_id == incident_id
    ).scalar() or 0
    
    has_thanked = db.query(IncidentThanks).filter(
        IncidentThanks.incident_id == incident_id,
        IncidentThanks.thanker_id == current_user.id
    ).first() is not None
    
    return {
        "incident_id": incident_id,
        "total_thanks": total,
        "has_thanked": has_thanked
    }


# ============== COMMENTS ENDPOINTS ==============

@router.post("/incidents/{incident_id}/comments")
async def add_comment(
    incident_id: str,
    request: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> CommentResponse:
    """Add a comment to an incident."""
    
    # Verify incident exists
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Create comment
    comment = IncidentComment(
        incident_id=incident_id,
        user_id=current_user.id,
        content=request.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Award points for commenting
    gamification_service.award_points(db, current_user.id, 1, "added_comment")
    
    return CommentResponse(
        id=comment.id,
        incident_id=comment.incident_id,
        content=comment.content,
        upvotes=0,
        created_at=comment.created_at,
        user={
            "id": current_user.id,
            "name": current_user.full_name or "Anonymous",
            "profile_photo_url": current_user.profile_photo_url,
            "trust_score": current_user.trust_score or 0
        },
        has_upvoted=False
    )


@router.get("/incidents/{incident_id}/comments")
async def get_comments(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get all comments for an incident."""
    
    comments = db.query(IncidentComment).filter(
        IncidentComment.incident_id == incident_id
    ).order_by(desc(IncidentComment.upvotes), desc(IncidentComment.created_at)).all()
    
    result = []
    for comment in comments:
        # Get comment author
        author = db.query(User).filter(User.id == comment.user_id).first()
        
        # Check if current user has upvoted
        has_upvoted = db.query(CommentUpvote).filter(
            CommentUpvote.comment_id == comment.id,
            CommentUpvote.user_id == current_user.id
        ).first() is not None
        
        result.append({
            "id": comment.id,
            "incident_id": comment.incident_id,
            "content": comment.content,
            "upvotes": comment.upvotes or 0,
            "created_at": comment.created_at.isoformat(),
            "user": {
                "id": author.id if author else None,
                "name": author.full_name if author else "Anonymous",
                "profile_photo_url": author.profile_photo_url if author else None,
                "trust_score": author.trust_score if author else 0
            },
            "has_upvoted": has_upvoted
        })
    
    return result


@router.post("/comments/{comment_id}/upvote")
async def upvote_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Upvote a comment."""
    
    comment = db.query(IncidentComment).filter(IncidentComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if already upvoted
    existing = db.query(CommentUpvote).filter(
        CommentUpvote.comment_id == comment_id,
        CommentUpvote.user_id == current_user.id
    ).first()
    
    if existing:
        # Remove upvote (toggle)
        db.delete(existing)
        comment.upvotes = max(0, (comment.upvotes or 0) - 1)
        action = "removed"
    else:
        # Add upvote
        upvote = CommentUpvote(
            comment_id=comment_id,
            user_id=current_user.id
        )
        db.add(upvote)
        comment.upvotes = (comment.upvotes or 0) + 1
        action = "added"
    
    db.commit()
    
    return {
        "success": True,
        "action": action,
        "upvotes": comment.upvotes
    }


# ============== MY STATS ==============

@router.get("/my-impact")
async def get_my_impact(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get user's social impact stats."""
    
    # Total thanks received
    thanks_received = db.query(func.count(IncidentThanks.id)).filter(
        IncidentThanks.reporter_id == current_user.id
    ).scalar() or 0
    
    # Total comments made
    comments_made = db.query(func.count(IncidentComment.id)).filter(
        IncidentComment.user_id == current_user.id
    ).scalar() or 0
    
    # Total upvotes received on comments
    user_comments = db.query(IncidentComment.id).filter(
        IncidentComment.user_id == current_user.id
    ).subquery()
    upvotes_received = db.query(func.sum(IncidentComment.upvotes)).filter(
        IncidentComment.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "thanks_received": thanks_received,
        "comments_made": comments_made,
        "upvotes_received": upvotes_received,
        "total_people_helped": current_user.total_people_helped or 0
    }


# ============== FOLLOW ENDPOINTS ==============

@router.post("/follow/{user_id}")
async def follow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Follow a user to get their reports first in your feed."""
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.followed_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    # Create follow
    follow = UserFollow(
        follower_id=current_user.id,
        followed_id=user_id
    )
    db.add(follow)
    db.commit()
    
    # Count new follower count
    follower_count = db.query(func.count(UserFollow.id)).filter(
        UserFollow.followed_id == user_id
    ).scalar() or 0
    
    return {
        "success": True,
        "message": f"Now following {target_user.full_name or 'this user'}",
        "follower_count": follower_count
    }


@router.delete("/follow/{user_id}")
async def unfollow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Unfollow a user."""
    
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.followed_id == user_id
    ).first()
    
    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    db.delete(follow)
    db.commit()
    
    return {
        "success": True,
        "message": "Unfollowed successfully"
    }


@router.get("/follow/{user_id}/status")
async def check_follow_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Check if current user is following a specific user."""
    
    is_following = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.followed_id == user_id
    ).first() is not None
    
    follower_count = db.query(func.count(UserFollow.id)).filter(
        UserFollow.followed_id == user_id
    ).scalar() or 0
    
    following_count = db.query(func.count(UserFollow.id)).filter(
        UserFollow.follower_id == user_id
    ).scalar() or 0
    
    return {
        "user_id": user_id,
        "is_following": is_following,
        "follower_count": follower_count,
        "following_count": following_count
    }


@router.get("/following")
async def get_following(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get list of users the current user is following."""
    
    follows = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id
    ).all()
    
    following_list = []
    for f in follows:
        user = db.query(User).filter(User.id == f.followed_id).first()
        if user:
            following_list.append({
                "id": user.id,
                "name": user.full_name or "Anonymous",
                "profile_photo_url": user.profile_photo_url,
                "trust_score": user.trust_score or 0
            })
    
    return {
        "count": len(following_list),
        "following": following_list
    }


@router.get("/followers")
async def get_followers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get list of users following the current user."""
    
    follows = db.query(UserFollow).filter(
        UserFollow.followed_id == current_user.id
    ).all()
    
    followers_list = []
    for f in follows:
        user = db.query(User).filter(User.id == f.follower_id).first()
        if user:
            followers_list.append({
                "id": user.id,
                "name": user.full_name or "Anonymous",
                "profile_photo_url": user.profile_photo_url,
                "trust_score": user.trust_score or 0
            })
    
    return {
        "count": len(followers_list),
        "followers": followers_list
    }

