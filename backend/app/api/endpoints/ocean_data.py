"""
Ocean data analysis endpoints
"""
from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse, StreamingResponse
import os
import shutil
from app.services.forecast import (
    plot_depth_vs_parameter,
    plot_combined_depth_parameters,
    plot_depth_vs_parameter_plotly,
    plot_combined_depth_parameters_plotly
)

router = APIRouter()

@router.post("/depth-profile")
async def visualize_depth(
    file: UploadFile = File(None),
    parameter: str = Query("chlorophyll", description="Parameter to visualize"),
    use_default_data: bool = Query(False),
    format: str = Query("interactive")
):
    """Generate depth profile visualization"""
    try:
        param_map = {
            "chlorophyll": "Chlorophyl",
            "ph": "pH",
            "salinity": "Salinity",
            "combined": "combined"
        }
        
        if parameter.lower() not in param_map:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid parameter. Choose from: {', '.join(param_map.keys())}"}
            )
        
        param = param_map[parameter.lower()]
        
        # Determine which file to use
        if use_default_data or file is None:
            depth_file = os.path.join("data", "MergedData.csv")
            if not os.path.exists(depth_file):
                return JSONResponse(
                    status_code=404,
                    content={"error": "Default depth dataset not found"}
                )
            file_path = depth_file
        else:
            # Save the uploaded file
            file_path = os.path.join("data", file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        # Generate visualization
        if param == "combined":
            if format.lower() == "interactive":
                fig = plot_combined_depth_parameters_plotly(file_path)
                if fig is None:
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Failed to create interactive combined visualization"}
                    )
                # Parse the JSON string into a Python object to avoid double-encoding
                try:
                    import json
                    plot_data = json.loads(fig.to_json())
                    
                    # Add display configuration to make it more user-friendly
                    plot_config = {
                        "displayModeBar": True,
                        "responsive": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
                    }
                    
                    # Return the processed data with structured format
                    return JSONResponse(
                        content={
                            "plot_data": plot_data,
                            "config": plot_config,
                            "title": "Ocean Depth Parameters Combined Visualization"
                        }
                    )
                except json.JSONDecodeError as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Error parsing plot JSON: {str(e)}"}
                    )
            else:
                plot_buffer = plot_combined_depth_parameters(file_path)
                return StreamingResponse(plot_buffer, media_type="image/png")
        else:
            if format.lower() == "interactive":
                fig = plot_depth_vs_parameter_plotly(file_path, param)
                if fig is None:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Failed to create interactive visualization for {param}"}
                    )
                # Parse the JSON string into a Python object to avoid double-encoding
                try:
                    import json
                    plot_data = json.loads(fig.to_json())
                    
                    # Add display configuration to make it more user-friendly
                    plot_config = {
                        "displayModeBar": True,
                        "responsive": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
                    }
                    
                    # Return the processed data with structured format
                    return JSONResponse(
                        content={
                            "plot_data": plot_data,
                            "config": plot_config,
                            "title": f"Ocean Depth vs {param} Visualization"
                        }
                    )
                except json.JSONDecodeError as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Error parsing plot JSON: {str(e)}"}
                    )
            else:
                plot_buffer = plot_depth_vs_parameter(file_path, param)
                return StreamingResponse(plot_buffer, media_type="image/png")
                
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing depth data: {str(e)}"}
        )
