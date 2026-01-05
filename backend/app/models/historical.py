from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base

class HistoricalIncidentStats(Base):
    __tablename__ = "historical_incident_stats"

    id = Column(Integer, primary_key=True, index=True)
    geohash = Column(String, index=True, nullable=False)  # Precision 6
    day_of_week = Column(Integer, nullable=False)         # 0=Mon, 6=Sun
    hour_of_day = Column(Integer, nullable=False)         # 0-23
    incident_count = Column(Integer, default=0)
    avg_severity = Column(Float, default=0.0)
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Compound index for efficient querying by location and time
    __table_args__ = (
        Index('ix_historical_stats_geo_time', 'geohash', 'day_of_week', 'hour_of_day'),
    )
