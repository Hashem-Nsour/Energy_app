from fastapi import APIRouter
from app.station import router as station_router
from app.session import router as session_router

api_router = APIRouter()

# Include the station and session routers with specific prefixes and tags
api_router.include_router(
    station_router,
    prefix="/stations",  # Prefix for station-related endpoints
    tags=["stations"],   # Documentation tag for station routes
)

api_router.include_router(
    session_router,
    prefix="/sessions",  # Prefix for session-related endpoints
    tags=["sessions"],   # Documentation tag for session routes
)

# You can easily add more routers here, for example:
# from app.other_module import router as other_router
# api_router.include_router(other_router, prefix="/other", tags=["other"])

