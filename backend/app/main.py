"""
Ehreezoh - Mobile-First Ride-Hailing Platform
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, incidents, users, health, drivers, rides, websocket, admin

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Ehreezoh API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create database tables (in production, use Alembic migrations)
    if settings.ENVIRONMENT == "development":
        logger.info("Creating database tables...")
        # Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ehreezoh API...")


# Initialize FastAPI app
app = FastAPI(
    title="Ehreezoh API",
    version=settings.APP_VERSION,
    description="""
## Mobile-First Ride-Hailing Platform for Cameroon

**Ehreezoh** connects passengers with moto-taxi and car drivers across Cameroon.

### Features
- 🚕 **Ride Hailing**: Request moto-taxis and cars on-demand
- 📍 **Real-time Tracking**: Live driver location updates
- 💰 **Mobile Money**: MTN Mobile Money and Orange Money integration
- ⭐ **Ratings**: Two-way rating system for drivers and passengers
- 🔒 **Secure**: Firebase Phone Authentication + JWT tokens

### Getting Started
1. **Register/Login**: Use `/api/v1/auth/register` or `/api/v1/auth/login`
2. **Get JWT Token**: Authenticate with Firebase phone number
3. **Make Requests**: Use JWT token in Authorization header
4. **Request Rides**: Use `/api/v1/rides/request` endpoint

### Authentication
Click the **Authorize** button (🔒) and enter: `Bearer YOUR_JWT_TOKEN`
    """,
    contact={
        "name": "Ehreezoh Support",
        "email": "support@ehreezoh.app",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and profile management with Firebase Phone Auth"
        },
        {
            "name": "Rides",
            "description": "Request, track, and manage rides (moto-taxi and cars)"
        },
        {
            "name": "Drivers",
            "description": "Driver registration, location updates, and availability management"
        },
        {
            "name": "Payments",
            "description": "Mobile Money payments and transaction management"
        },
        {
            "name": "Health",
            "description": "API health check and status endpoints"
        },
    ],
    lifespan=lifespan
)

# Middleware
# Custom CORS handler - more reliable than CORSMiddleware
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to all responses"""
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response
    
    # Process the request
    response = await call_next(request)
    
    # Add CORS headers to the response
    origin = request.headers.get("origin", "*")
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(drivers.router, prefix="/api/v1")
app.include_router(rides.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs" if settings.DEBUG else None
    }


# WebSocket endpoint (to be implemented)
@app.websocket("/ws/incidents")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time incident updates"""
    # To be implemented in Week 9-10
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )

