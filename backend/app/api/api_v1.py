"""
API router for all endpoints
"""
from fastapi import APIRouter
from app.api.endpoints import fish, edna, forecast, ocean_data

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(fish.router, prefix="/fish", tags=["Fish Analysis"])
api_router.include_router(edna.router, prefix="/edna", tags=["eDNA Analysis"])
api_router.include_router(forecast.router, prefix="/forecast", tags=["Forecasting"])
api_router.include_router(ocean_data.router, prefix="/ocean", tags=["Ocean Data"])
