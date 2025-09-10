"""
Ocean forecasting endpoints
"""
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
import os
import shutil
import pandas as pd
import io
import json
from app.services.forecast import (
    run_prophet,
    prepare_df,
    generate_depth_plots
)

router = APIRouter()

@router.post("/")
async def generate_forecast(
    files: List[UploadFile] = File(None),
    date_col: str = Query(None, description="Optional name of the date column (auto-detected if not provided)"),
    target_col: str = Query(None, description="Optional name of the target column to forecast (auto-detected if not provided)"),
    future_days: int = Query(30, description="Number of days to forecast into the future"),
    use_default_data: bool = Query(False, description="Set to true to use default SST dataset instead of uploaded files"),
    format: str = Query("future_interactive", description="Output format: 'future_interactive' for dynamic chart, 'future_image' for static PNG")
):
    """
    Generate comprehensive forecast visualization from time series data.
    
    This endpoint produces forecasts that clearly distinguish between historical data and future predictions.
    It supports both interactive visualizations and static images.
    """
    try:
        # Use default data if requested or no files provided
        if use_default_data or files is None or len(files) == 0:
            sst_file = os.path.join("data", "SST_Final.csv")
            if not os.path.exists(sst_file):
                return JSONResponse(
                    status_code=404,
                    content={"error": "Default dataset not found"}
                )
            
            result = run_prophet(
                file_path=sst_file,
                future_periods=future_days,
                save_csv_path=os.path.join("data", "forecast_output.csv"),
                save_plots=False
            )
        
        else:
            # Process uploaded files
            file_paths = []
            for file in files:
                file_path = os.path.join("data", file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                file_paths.append(file_path)
            
            # Run forecast
            result = run_prophet(
                file_path=file_paths[0],
                future_periods=future_days,
                date_col=date_col,
                target_col=target_col,
                save_csv_path=os.path.join("data", "forecast_output.csv"),
                save_plots=False
            )
        
        # Handle different output formats - prioritize future forecast visualizations
        if format.lower() == "future_interactive" or format.lower() == "interactive":
            # Return interactive future forecast visualization
            if "future_forecast_plot_json" in result and result["future_forecast_plot_json"] is not None:
                try:
                    future_plot_data = json.loads(result["future_forecast_plot_json"])
                    return JSONResponse(content=future_plot_data)
                except json.JSONDecodeError as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Error parsing future forecast plot JSON: {str(e)}"}
                    )
            # Fall back to regular interactive visualization if future is not available
            elif "forecast_plot_json" in result and result["forecast_plot_json"] is not None:
                try:
                    plot_data = json.loads(result["forecast_plot_json"])
                    return JSONResponse(content=plot_data)
                except json.JSONDecodeError as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Error parsing forecast plot JSON: {str(e)}"}
                    )
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "No forecast visualization data available"}
                )
        elif format.lower() == "future_image" or format.lower() == "image":
            # Use the specialized future forecast visualization
            if "future_forecast_plot" in result and result["future_forecast_plot"] is not None:
                return StreamingResponse(result["future_forecast_plot"], media_type="image/png")
            # Fall back to regular forecast plot if future is not available
            elif "forecast_plot" in result:
                return StreamingResponse(result["forecast_plot"], media_type="image/png")
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "No forecast visualization available"}
                )
        else:
            # Default to future forecast image
            if "future_forecast_plot" in result and result["future_forecast_plot"] is not None:
                return StreamingResponse(result["future_forecast_plot"], media_type="image/png")
            elif "forecast_plot" in result:
                return StreamingResponse(result["forecast_plot"], media_type="image/png")
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "No forecast visualization available"}
                )
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Error generating forecast: {str(e)}",
                "details": error_details
            }
        )

# The GET endpoint /future-forecast has been consolidated into the POST endpoint / 
# with improved functionality for both standard and future forecasts
