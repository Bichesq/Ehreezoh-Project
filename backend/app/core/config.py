"""
Application configuration
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Cameroon Traffic App"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/traffic_app"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-credentials.json"
    FIREBASE_PROJECT_ID: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8081"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    UPLOAD_DIR: str = "./uploads"
    
    # Image Storage
    STORAGE_TYPE: str = "local"  # local, s3, cloudinary
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_REGION: str = "eu-west-1"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Rate Limiting
    RATE_LIMIT_ANONYMOUS: str = "3/day"
    RATE_LIMIT_REGISTERED: str = "10/day"
    RATE_LIMIT_TRUSTED: str = "20/day"
    
    # Incident Settings
    INCIDENT_EXPIRY_TRAFFIC_JAM: int = 1800  # 30 minutes
    INCIDENT_EXPIRY_ACCIDENT: int = 14400  # 4 hours
    INCIDENT_EXPIRY_ROAD_HAZARD: int = 86400  # 24 hours
    INCIDENT_AUTO_HIDE_THRESHOLD: int = -5
    INCIDENT_ABUSE_REPORT_THRESHOLD: int = 5
    
    # Geospatial
    DEFAULT_SEARCH_RADIUS: int = 5000  # 5km
    MAX_SEARCH_RADIUS: int = 50000  # 50km
    LOCATION_FUZZING_METERS: int = 50
    
    # Push Notifications
    FCM_SERVER_KEY: str = ""
    
    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@trafficcm.app"
    
    # Admin
    ADMIN_EMAIL: str = "admin@trafficcm.app"
    ADMIN_PHONE: str = "+237000000000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

