"""
Weekly Digest API - generates personalized weekly summaries
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.incident import Incident
from app.models.social import IncidentThanks, UserFollow

router = APIRouter(prefix="/digest", tags=["Digest"])


@router.get("/weekly")
async def get_weekly_digest(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get this week's personalized digest for the user."""
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # User's contributions this week
    my_reports = db.query(func.count(Incident.id)).filter(
        Incident.reporter_id == current_user.id,
        Incident.created_at >= week_ago
    ).scalar() or 0
    
    my_thanks_received = db.query(func.count(IncidentThanks.id)).filter(
        IncidentThanks.reporter_id == current_user.id,
        IncidentThanks.created_at >= week_ago
    ).scalar() or 0
    
    # New followers this week
    new_followers = db.query(func.count(UserFollow.id)).filter(
        UserFollow.followed_id == current_user.id,
        UserFollow.created_at >= week_ago
    ).scalar() or 0
    
    # Community stats this week
    total_incidents = db.query(func.count(Incident.id)).filter(
        Incident.created_at >= week_ago
    ).scalar() or 0
    
    total_thanks = db.query(func.count(IncidentThanks.id)).filter(
        IncidentThanks.created_at >= week_ago
    ).scalar() or 0
    
    # Followed users' activity
    followed_ids = db.query(UserFollow.followed_id).filter(
        UserFollow.follower_id == current_user.id
    ).subquery()
    
    followed_reports = db.query(func.count(Incident.id)).filter(
        Incident.reporter_id.in_(followed_ids),
        Incident.created_at >= week_ago
    ).scalar() or 0
    
    # Top reporter this week (most reports)
    top_reporter_data = db.query(
        Incident.reporter_id,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.created_at >= week_ago
    ).group_by(Incident.reporter_id).order_by(func.count(Incident.id).desc()).first()
    
    top_reporter = None
    if top_reporter_data:
        user = db.query(User).filter(User.id == top_reporter_data[0]).first()
        if user:
            top_reporter = {
                "id": user.id,
                "name": user.full_name or "Anonymous",
                "report_count": top_reporter_data[1]
            }
    
    # Generate highlight message
    highlights = []
    if my_reports > 0:
        highlights.append(f"You reported {my_reports} incident{'s' if my_reports > 1 else ''}")
    if my_thanks_received > 0:
        highlights.append(f"{my_thanks_received} people thanked you")
    if new_followers > 0:
        highlights.append(f"You gained {new_followers} new follower{'s' if new_followers > 1 else ''}")
    
    return {
        "period": {
            "start": week_ago.isoformat(),
            "end": datetime.utcnow().isoformat()
        },
        "my_stats": {
            "reports_made": my_reports,
            "thanks_received": my_thanks_received,
            "new_followers": new_followers
        },
        "community_stats": {
            "total_incidents": total_incidents,
            "total_thanks": total_thanks,
            "followed_reports": followed_reports
        },
        "top_reporter": top_reporter,
        "highlights": highlights,
        "message": " • ".join(highlights) if highlights else "Stay active to see your highlights!"
    }
