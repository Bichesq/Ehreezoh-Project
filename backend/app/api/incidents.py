"""
Incidents endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()


class IncidentResponse(BaseModel):
    """Incident response model"""
    id: str
    type: str
    location: dict
    severity: int
    description: Optional[str]
    image_url: Optional[str]
    upvotes: int
    downvotes: int
    net_votes: int
    verified: bool
    distance_meters: Optional[float]
    created_at: str
    expires_at: str


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_incident(
    type: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    severity: int = Form(3),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new incident report
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement incident creation
    # 1. Validate incident type
    # 2. Validate coordinates
    # 3. Process and upload image
    # 4. Create incident in database
    # 5. Update cache
    # 6. Broadcast via WebSocket
    # 7. Send push notifications
    
    return {
        "success": True,
        "data": {
            "incident_id": "placeholder-uuid",
            "type": type,
            "location": {"lat": latitude, "lng": longitude},
            "severity": severity,
            "expires_at": "2025-11-11T11:00:00Z",
            "created_at": "2025-11-11T10:30:00Z"
        }
    }


@router.get("/nearby")
async def get_nearby_incidents(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    radius: int = Query(5000, description="Search radius in meters", le=50000),
    types: Optional[str] = Query(None, description="Comma-separated incident types"),
    limit: int = Query(50, description="Maximum number of results", le=200),
    db: Session = Depends(get_db)
):
    """
    Get incidents near a location
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement geospatial query
    # 1. Parse incident types filter
    # 2. Query PostGIS for incidents within radius
    # 3. Filter by status (active only)
    # 4. Calculate distances
    # 5. Sort by distance
    # 6. Return paginated results
    
    return {
        "success": True,
        "data": {
            "incidents": [
                {
                    "id": "placeholder-uuid-1",
                    "type": "traffic_jam",
                    "location": {"lat": latitude + 0.01, "lng": longitude + 0.01},
                    "severity": 3,
                    "description": "Heavy traffic on main road",
                    "image_url": None,
                    "upvotes": 5,
                    "downvotes": 0,
                    "net_votes": 5,
                    "verified": False,
                    "distance_meters": 1250,
                    "created_at": "2025-11-11T10:00:00Z",
                    "expires_at": "2025-11-11T10:30:00Z"
                }
            ],
            "meta": {
                "count": 1,
                "radius_km": radius / 1000
            }
        }
    }


@router.patch("/{incident_id}/vote")
async def vote_incident(
    incident_id: str,
    vote_type: str,
    db: Session = Depends(get_db)
):
    """
    Upvote or downvote an incident
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement voting
    # 1. Validate vote_type (upvote/downvote)
    # 2. Check if user already voted
    # 3. Create or update vote
    # 4. Update incident vote counts
    # 5. Check auto-hide threshold
    # 6. Broadcast update via WebSocket
    
    return {
        "success": True,
        "data": {
            "incident_id": incident_id,
            "upvotes": 6,
            "downvotes": 0,
            "net_votes": 6,
            "user_vote": vote_type
        }
    }


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an incident (only by reporter)
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement incident deletion
    # 1. Verify user is the reporter
    # 2. Delete incident from database
    # 3. Delete associated image
    # 4. Update cache
    # 5. Broadcast removal via WebSocket
    
    return None


@router.post("/{incident_id}/report", status_code=status.HTTP_201_CREATED)
async def report_incident(
    incident_id: str,
    reason: str,
    details: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Report an incident as false/spam/inappropriate
    
    This endpoint will be fully implemented in Week 3-4
    """
    # TODO: Implement abuse reporting
    # 1. Validate reason
    # 2. Create abuse report
    # 3. Increment incident report count
    # 4. Check auto-hide threshold
    # 5. Flag for manual review if needed
    
    return {
        "success": True,
        "message": "Report submitted successfully"
    }

