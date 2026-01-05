"""
Community API endpoints - Verification, Leaderboards, Neighborhoods
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.incident import Incident
from app.models.community import City, Neighborhood, IncidentVerification
from app.services.gamification import gamification_service

router = APIRouter(prefix="/community", tags=["Community"])


# ============== SCHEMAS ==============

class VerifyRequest(BaseModel):
    verification_type: str  # 'still_there' or 'all_clear'

class VerificationResponse(BaseModel):
    success: bool
    message: str
    new_status: Optional[str] = None
    
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    full_name: str
    points: int
    trust_score: int
    total_reports: int
    profile_photo_url: Optional[str] = None

    class Config:
        orm_mode = True


# ============== VERIFICATION ENDPOINTS ==============

@router.post("/incidents/{incident_id}/verify")
async def verify_incident(
    incident_id: str,
    request: VerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> VerificationResponse:
    """
    Verify an incident with 'still_there' or 'all_clear'.
    Requires trust_score >= 25 to verify.
    """
    
    # Check trust requirement
    MIN_TRUST_TO_VERIFY = 25
    user_trust = current_user.trust_score or 0
    if user_trust < MIN_TRUST_TO_VERIFY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Trust Score must be at least {MIN_TRUST_TO_VERIFY} to verify incidents."
        )
    
    # Get incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident.status != 'active':
        raise HTTPException(status_code=400, detail="Can only verify active incidents")
    
    # Check if user already verified this incident
    existing = db.query(IncidentVerification).filter(
        IncidentVerification.incident_id == incident_id,
        IncidentVerification.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already verified this incident")
    
    # Validate verification type
    if request.verification_type not in ['still_there', 'all_clear']:
        raise HTTPException(status_code=400, detail="Invalid verification type")
    
    # Calculate verification weight based on trust score
    weight = max(0.1, user_trust / 100.0)
    
    # Create verification
    verification = IncidentVerification(
        incident_id=incident_id,
        user_id=current_user.id,
        verification_type=request.verification_type,
        weight=weight
    )
    db.add(verification)
    
    # Update incident based on verifications
    if request.verification_type == 'still_there':
        incident.confirmations = (incident.confirmations or 0) + 1
        
        # Check if incident should become verified
        # Sum weights of 'still_there' verifications
        total_weight = db.query(func.sum(IncidentVerification.weight)).filter(
            IncidentVerification.incident_id == incident_id,
            IncidentVerification.verification_type == 'still_there'
        ).scalar() or 0
        total_weight += weight  # Include current
        
        if total_weight >= 3.0 and not incident.is_verified:
            incident.is_verified = True
            incident.verified_at = datetime.utcnow()
            
            # Award bonus points to original reporter
            if incident.user_id:
                reporter = db.query(User).filter(User.id == incident.user_id).first()
                if reporter:
                    reporter.trust_score = min(1000, (reporter.trust_score or 0) + 10)
                    gamification_service.award_points(db, incident.user_id, 10, "report_verified")
        
        message = "Thanks for confirming! Report verified." if incident.is_verified else "Thanks for confirming!"
        
    else:  # all_clear
        # Count 'all_clear' verifications
        clear_count = db.query(func.count(IncidentVerification.id)).filter(
            IncidentVerification.incident_id == incident_id,
            IncidentVerification.verification_type == 'all_clear'
        ).scalar() or 0
        clear_count += 1  # Include current
        
        if clear_count >= 3:
            incident.status = 'resolved'
            message = "Incident marked as resolved. Thanks!"
        else:
            message = "Thanks for the update!"
    
    db.commit()
    
    # Award points to verifier
    gamification_service.award_points(db, current_user.id, 2, "incident_verification")
    
    return VerificationResponse(
        success=True,
        message=message,
        new_status=incident.status
    )


# ============== LEADERBOARD ENDPOINTS ==============

@router.get("/leaderboard")
async def get_leaderboard(
    scope: str = "city",
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """
    Get leaderboard. Scope can be 'city' or 'global'.
    """
    
    # For now, return global leaderboard sorted by points
    users = db.query(User).filter(
        User.is_active == True,
        User.total_reports > 0
    ).order_by(desc(User.points)).limit(limit).all()
    
    result = []
    for rank, user in enumerate(users, 1):
        result.append({
            "rank": rank,
            "user_id": user.id,
            "full_name": user.full_name or "Anonymous",
            "points": user.points or 0,
            "trust_score": user.trust_score or 0,
            "total_reports": user.total_reports or 0,
            "profile_photo_url": user.profile_photo_url,
            "is_current_user": user.id == current_user.id
        })
    
    return result


@router.get("/my-rank")
async def get_my_rank(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get current user's rank in the leaderboard.
    """
    
    # Count users with more points
    users_above = db.query(func.count(User.id)).filter(
        User.is_active == True,
        User.points > (current_user.points or 0)
    ).scalar()
    
    rank = (users_above or 0) + 1
    
    # Count total active contributors
    total = db.query(func.count(User.id)).filter(
        User.is_active == True,
        User.total_reports > 0
    ).scalar()
    
    return {
        "rank": rank,
        "total_contributors": total or 0,
        "points": current_user.points or 0,
        "trust_score": current_user.trust_score or 0,
        "percentile": round((1 - rank / max(total or 1, 1)) * 100, 1) if total else 0
    }


# ============== STATS ENDPOINTS ==============

@router.get("/stats")
async def get_community_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get community-wide statistics.
    """
    
    total_reports = db.query(func.count(Incident.id)).scalar() or 0
    active_reports = db.query(func.count(Incident.id)).filter(
        Incident.status == 'active'
    ).scalar() or 0
    verified_reports = db.query(func.count(Incident.id)).filter(
        Incident.is_verified == True
    ).scalar() or 0
    total_contributors = db.query(func.count(User.id)).filter(
        User.total_reports > 0
    ).scalar() or 0
    
    return {
        "total_reports": total_reports,
        "active_reports": active_reports,
        "verified_reports": verified_reports,
        "total_contributors": total_contributors,
        "verification_rate": round(verified_reports / max(total_reports, 1) * 100, 1)
    }
