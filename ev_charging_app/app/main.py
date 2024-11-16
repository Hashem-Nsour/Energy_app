from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.api_router import api_router  # Ensure api_router correctly includes all API routes
from app.ocpp_server import ocpp_server
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="OCPP Charging Station API",
    description="API for managing charging stations and OCPP connections",
    version="1.0.0",
)

# CORS middleware for allowing cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    """
    Event triggered when the application starts.
    Ensures the database is initialized.
    """
    logger.info("Starting application...")
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Database initialized successfully.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Event triggered when the application shuts down.
    Cleans up any resources if necessary.
    """
    logger.info("Shutting down application...")

# Include API routers
app.include_router(api_router, prefix="/api", tags=["API Routes"])

# WebSocket endpoint for OCPP connections
@app.websocket("/ocpp/{charge_point_id}")
async def ocpp_websocket_endpoint(websocket: WebSocket, charge_point_id: str):
    """
    WebSocket endpoint to handle OCPP connections from charging stations.
    """
    logger.info(f"New WebSocket connection initiated for charge point: {charge_point_id}")
    await websocket.accept()
    try:
        await ocpp_server(websocket, charge_point_id)
    except WebSocketDisconnect:
        logger.warning(f"WebSocket disconnected for charge point: {charge_point_id}")
    except Exception as e:
        logger.error(f"Error during WebSocket communication with charge point {charge_point_id}: {e}")
    finally:
        logger.info(f"WebSocket session ended for charge point: {charge_point_id}")
