"""
Fish-related endpoints including classification and stock prediction
"""
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse, StreamingResponse
import os
from app.services.fish_classification import predict_image
from app.services.stock_prediction import (
    generate_forecast_chart,
    generate_health_check_chart,
    calculate_sustainability_metrics
)
import json

router = APIRouter()

@router.post("/classify")
async def classify_fish(file: UploadFile = File(...)):
    """Classify a fish image"""
    try:
        # Save the uploaded file temporarily
        temp_path = os.path.join("data", file.filename)
        with open(temp_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Predict the class
        predicted_class, confidence = predict_image(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error classifying fish: {str(e)}"}
        )

@router.get("/stock/forecast")
def get_stock_forecast(use_default_data: bool = Query(True)):
    """Get fish stock forecast visualization"""
    try:
        chart_json = generate_forecast_chart()
        return JSONResponse(content=json.loads(chart_json))
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating forecast: {str(e)}"}
        )

@router.get("/stock/health")
def get_stock_health(use_default_data: bool = Query(True)):
    """Get fish stock health check visualization"""
    try:
        image_buffer = generate_health_check_chart()
        return StreamingResponse(image_buffer, media_type="image/png")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating health check: {str(e)}"}
        )

@router.get("/stock/metrics")
def get_stock_metrics(use_default_data: bool = Query(True)):
    """Get fish stock sustainability metrics"""
    try:
        metrics = calculate_sustainability_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error calculating metrics: {str(e)}"}
        )