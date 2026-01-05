from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.route import RouteAnalysisRequest, RouteAnalysisResponse
from app.services.route_analysis import route_analysis_service
from app.models.permission import UserPermission

router = APIRouter(prefix="/routes", tags=["Routes"])

def get_user_permissions(user: User, db: Session) -> list[str]:
    # Fetch active permissions for user
    perms = db.query(UserPermission).filter(
        UserPermission.user_id == user.id,
        UserPermission.is_active == True
    ).all()
    # In real world, check expiry too
    return [p.permission_type for p in perms]

@router.post("/analyze", response_model=RouteAnalysisResponse)
async def analyze_routes(
    request: RouteAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze and score routes between origin and destination based on active incidents
    """
    
    # Permission check for police checkpoints
    user_perms = get_user_permissions(current_user, db)
    
    if request.preferences.show_police_checkpoints:
        if "view_police_checkpoints" not in user_perms:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view police checkpoints"
            )
    
    routes = await route_analysis_service.analyze_routes(
        origin=request.origin,
        destination=request.destination,
        ride_type=request.ride_type,
        preferences=request.preferences,
        db=db,
        user_permissions=user_perms
    )
    
    recommendation = routes[0].id if routes else None
    
    return {
        "routes": routes,
        "recommendation": recommendation
    }
