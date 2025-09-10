"""
Main application module for Ocean AI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import PROJECT_NAME, VERSION, DESCRIPTION
from app.core.routes import configure_routes
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the FastAPI application
app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint to verify server is running"""
    return {"status": "running", "message": "Ocean AI Backend is operational"}

# Configure routes
api_router = configure_routes()
app.include_router(api_router, prefix="/api/v1")
