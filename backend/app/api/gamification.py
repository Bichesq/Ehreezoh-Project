from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gamification import gamification_service
from app.api import auth
from app.core.auth import get_current_user
from app.models.gamification import UserBadge
from app.models.user import User
from typing import List, Dict, Any

router = APIRouter()

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    users = gamification_service.get_leaderboard(db)
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "points": u.points,
            "reputation_score": u.reputation_score,
            "profile_photo_url": u.profile_photo_url
        }
        for u in users
    ]

@router.get("/me")
def get_my_gamification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.gamification import Badge

    # 1. Fetch all badges and user's earned badges
    all_badges = db.query(Badge).all()
    user_badges = db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    earned_badge_ids = {ub.badge_id: ub.earned_at for ub in user_badges}
    
    # 2. Format badges with status
    badges_data = []
    for badge in all_badges:
        earned_date = earned_badge_ids.get(badge.id)
        badges_data.append({
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon_url,
            "is_earned": earned_date is not None,
            "earned_at": earned_date,
            "requirement_value": badge.requirement_value,
            "requirement_type": badge.requirement_type
        })
    
    # 3. Calculate Trust Level & Progress
    trust_score = current_user.trust_score or 0
    
    levels = [
        (0, "Newcomer", "🌱"),
        (50, "Trusted", "✅"),
        (150, "Guardian", "🛡️"),
        (300, "Elder", "🦁"),
        (500, "Legend", "👑"),
    ]
    
    current_level_name = "Newcomer"
    current_level_icon = "🌱"
    next_level_score = 50
    
    for score, name, icon in levels:
        if trust_score >= score:
            current_level_name = name
            current_level_icon = icon
        if score > trust_score:
            next_level_score = score
            break
            
    # If max level
    if trust_score >= 500:
        next_level_score = None
    
    return {
        "points": current_user.points,
        "reputation_score": current_user.reputation_score,
        "trust_score": trust_score,
        "trust_level": current_level_name,
        "trust_icon": current_level_icon,
        "next_level_score": next_level_score,
        "total_reports": current_user.total_reports or 0,
        "total_people_helped": current_user.total_people_helped or 0,
        "current_streak": current_user.current_streak or 0,
        "longest_streak": current_user.longest_streak or 0,
        "badges": badges_data
    }

@router.post("/seed")
def seed_gamification(db: Session = Depends(get_db)):
    gamification_service.seed_badges(db)
    return {"status": "seeded"}

@router.post("/test-award-points")
def test_award(points: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_total = gamification_service.award_points(db, current_user.id, points)
    return {"status": "awarded", "new_total": new_total}
