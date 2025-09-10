# backend/main.py
from fastapi import FastAPI, UploadFile, File, Query, Path
from typing import List, Optional
import os, shutil
import pandas as pd
import io
from fastapi.responses import StreamingResponse, JSONResponse

# Import forecast logic
from services.forecast import (
    run_prophet, 
    prepare_df, 
    generate_depth_plots, 
    plot_depth_vs_parameter,
    plot_combined_depth_parameters,
    plot_depth_vs_parameter_plotly,
    plot_combined_depth_parameters_plotly
)

# Import eDNA logic
from services.edna_analysis import analyze_edna, check_invasive
from models.edna_manager import init_model, get_model, train_new_model

# Import fish stock prediction logic
from services.stock_prediction import (
    generate_forecast_chart,
    generate_health_check_chart,
    calculate_sustainability_metrics
)

# Import fish classification logic
from services.fish_classification import predict_image

# Import plotly
import plotly.graph_objects as go
import plotly.express as px
import json

# Create FastAPI app with custom title and description
app = FastAPI(
    title="Ocean AI Analysis API",
    description="API for ocean data analysis, forecasting, eDNA analysis, and fish stock prediction",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility function for creating interactive plots
def create_plotly_depth_visualization(file_path, parameter_name):
    """
    Create an interactive Plotly visualization for depth vs parameter
    
    Args:
        file_path: Path to the CSV file with depth data
        parameter_name: The parameter to plot (e.g., 'Chlorophyl', 'pH', 'Salinity')
        
    Returns:
        A Plotly figure object
    """
    try:
        # Read the data
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = [str(c).replace('.','_').replace(' ','_') for c in df.columns]
        
        # Sort by depth for a clearer plot
        df = df.sort_values('Depth')
        
        # Create a Plotly figure
        fig = px.scatter(
            df, 
            x=parameter_name, 
            y='Depth',
            title=f'Depth vs {parameter_name}',
            labels={parameter_name: parameter_name, 'Depth': 'Depth (m)'}
        )
        
        # Add line to connect points
        fig.add_trace(go.Scatter(
            x=df[parameter_name], 
            y=df['Depth'],
            mode='lines',
            line=dict(color='rgba(0,0,0,0.3)'),
            showlegend=False
        ))
        
        # Customize the layout
        fig.update_layout(
            yaxis=dict(autorange="reversed"),  # Reverse y-axis (depth increases downward)
            height=600,
            width=800,
            template="plotly_white",
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add hover template
        fig.update_traces(
            hovertemplate=f"{parameter_name}: %{{x:.3f}}<br>Depth: %{{y:.1f}} m<extra></extra>"
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating Plotly visualization: {str(e)}")
        return None

# Utility function for creating interactive forecast plots
def create_plotly_forecast_visualization(forecast_df, historical_df=None):
    """
    Create an interactive Plotly visualization for time series forecasts
    
    Args:
        forecast_df: DataFrame containing forecast results with ds, yhat, yhat_lower, yhat_upper columns
        historical_df: Optional DataFrame containing historical values with ds and y columns
        
    Returns:
        A Plotly figure object
    """
    try:
        # Create a Plotly figure
        fig = go.Figure()
        
        # Add historical data if provided
        if historical_df is not None:
            fig.add_trace(go.Scatter(
                x=historical_df['ds'],
                y=historical_df['y'],
                mode='markers+lines',
                name='Historical',
                line=dict(color='blue'),
                marker=dict(color='blue', size=4)
            ))
        
        # Add forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='red')
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'].tolist() + forecast_df['ds'].tolist()[::-1],
            y=forecast_df['yhat_upper'].tolist() + forecast_df['yhat_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,0,0,0)'),
            name='Confidence Interval'
        ))
        
        # Customize layout
        fig.update_layout(
            title='Time Series Forecast',
            xaxis_title='Date',
            yaxis_title='Value',
            height=600,
            width=1000,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode="x unified"
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating Plotly forecast visualization: {str(e)}")
        return None

# ---------------- Root ----------------
@app.get("/")
def root():
    return {"message": "Ocean AI Backend running with Forecast + eDNA + Fish Stock Analysis"}

# ---------------- Visualization and Analysis Endpoints ----------------

@app.post("/visualize/forecast",
          summary="Generate Forecast Visualization",
          description="Upload time series data or use default data to generate a forecast visualization showing historical data and future trends.")
async def visualize_forecast(
    files: List[UploadFile] = File(None), 
    date_col: str = Query(None, description="Optional name of the date column (auto-detected if not provided)"), 
    target_col: str = Query(None, description="Optional name of the target column to forecast (auto-detected if not provided)"), 
    future_days: int = Query(90, description="Number of days to forecast into the future"),
    use_default_data: bool = Query(True, description="Set to true to use default dataset instead of uploaded files"),
    format: str = Query("future_interactive", description="Output format: 'future_interactive' for a dynamic chart or 'future_image' for a static PNG.")
):
    """
    Generate a comprehensive forecast visualization using uploaded data or a default dataset.
    The visualization will show historical data, model fit, and future trends.
    
    Parameters:
    - files: Optional list of files to upload. The first file is used for forecasting, a second can be a regressor.
    - date_col: Optional name of the date column.
    - target_col: Optional name of the target column to forecast.
    - future_days: Number of days to forecast into the future.
    - use_default_data: Set to True to use the default SST dataset.
    - format: 'future_interactive' (default) or 'future_image'.
    """
    try:
        file_to_process = None
        regressor_file = None

        # Determine which data to use
        if use_default_data or not files:
            print("Using default dataset for forecast")
            sst_file = os.path.join(UPLOAD_FOLDER, "SST_Final.csv")
            if not os.path.exists(sst_file):
                return JSONResponse(
                    status_code=404,
                    content={"error": "Default SST dataset not found. Please upload data or ensure it exists."}
                )
            file_to_process = sst_file
        else:
            # Process uploaded files
            print(f"Received forecast request with {len(files)} files")
            file_paths = []
            for file in files:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                file_paths.append(file_path)

            file_to_process = file_paths[0]
            if len(file_paths) > 1:
                regressor_file = file_paths[1]

        print(f"Using main file: {file_to_process}")
        if regressor_file:
            print(f"Using regressor file: {regressor_file}")

        # Run the Prophet forecasting model
        result = run_prophet(
            file_path=file_to_process,
            regressor_file_path=regressor_file,
            date_col=date_col,
            target_col=target_col,
            future_periods=future_days,
            save_csv_path=os.path.join(UPLOAD_FOLDER, "forecast_output.csv"),
            save_plots=False  # Ensure plots are generated in memory
        )

        # Return the requested format
        if format.lower() == "future_interactive" or format.lower() == "interactive":
            # Use the enhanced future forecast JSON
            if "future_forecast_plot_json" in result and result["future_forecast_plot_json"]:
                return JSONResponse(content=json.loads(result["future_forecast_plot_json"]))
            # Fall back to regular interactive visualization if future is not available
            elif "forecast_plot_json" in result and result["forecast_plot_json"]:
                return JSONResponse(content=json.loads(result["forecast_plot_json"]))
            else:
                return JSONResponse(status_code=500, content={"error": "Interactive forecast visualization is not available."})

        elif format.lower() == "future_image" or format.lower() == "image":
            # Use the enhanced future forecast image
            if "future_forecast_plot" in result and result["future_forecast_plot"]:
                return StreamingResponse(result["future_forecast_plot"], media_type="image/png")
            # Fall back to regular forecast plot if future is not available
            elif "forecast_plot" in result:
                return StreamingResponse(result["forecast_plot"], media_type="image/png")
            else:
                return JSONResponse(status_code=500, content={"error": "Forecast image is not available."})

        else:
            # Default to future forecast
            if "future_forecast_plot" in result and result["future_forecast_plot"]:
                return StreamingResponse(result["future_forecast_plot"], media_type="image/png")
            elif "forecast_plot" in result:
                return StreamingResponse(result["forecast_plot"], media_type="image/png")
            else:
                return JSONResponse(status_code=400, content={"error": "Invalid format. Please use 'future_interactive' or 'future_image'."})

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in forecast processing: {str(e)}\nDetails: {error_details}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "details": error_details}
        )

@app.post("/visualize/depth",
          summary="Generate Depth Profile Visualization",
          description="Upload depth data or use default data to generate a depth profile visualization")
async def visualize_depth(
    file: UploadFile = File(None),
    parameter: str = Query("chlorophyll", description="Parameter to visualize: chlorophyll, ph, salinity, or combined"),
    use_default_data: bool = Query(False, description="Set to true to use default dataset instead of uploaded file"),
    format: str = Query("interactive", description="Output format: 'interactive' for Plotly JSON or 'image' for static PNG")
):
    """
    Generate a depth profile visualization using uploaded data or default dataset.
    
    Parameters:
    - file: Optional file containing depth and parameter data
    - parameter: The parameter to plot (chlorophyll, ph, salinity, or combined)
    - use_default_data: Set to True to use default dataset instead of uploaded file
    - format: Output format - 'interactive' for Plotly JSON (default) or 'image' for static PNG
    """
    try:
        # Map the parameter name
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
            print("Using default dataset for depth visualization")
            depth_file = os.path.join(UPLOAD_FOLDER, "MergedData.csv")
            if not os.path.exists(depth_file):
                return JSONResponse(
                    status_code=404,
                    content={"error": "Default depth dataset not found. Please upload data first or provide a file."}
                )
            file_path = depth_file
        else:
            # Save the uploaded file
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        # Generate visualization based on requested format and parameter
        if param == "combined":
            if format.lower() == "interactive":
                # Create interactive combined Plotly visualization
                fig = plot_combined_depth_parameters_plotly(file_path)
                if fig is None:
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Failed to create interactive combined visualization"}
                    )
                
                try:    
                    # Parse the JSON string into a Python object to avoid double-encoding
                    plot_data = json.loads(fig.to_json())
                    
                    # Add display configuration to make it more user-friendly
                    plot_config = {
                        "displayModeBar": True,
                        "responsive": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
                    }
                    
                    # Return the processed data
                    return JSONResponse(
                        content={
                            "plot_data": plot_data,
                            "config": plot_config,
                            "title": "Ocean Depth Parameters Visualization"
                        }
                    )
                except json.JSONDecodeError as e:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Error parsing combined plot JSON: {str(e)}"}
                    )
            else:
                # Generate static combined image plot
                plot_buffer = plot_combined_depth_parameters(file_path)
                return StreamingResponse(plot_buffer, media_type="image/png")
        else:
            # Single parameter visualization
            if format.lower() == "interactive":
                # Create interactive Plotly visualization for a single parameter
                fig = plot_depth_vs_parameter_plotly(file_path, param)
                if fig is None:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Failed to create interactive visualization for {parameter}"}
                    )
                
                try:
                    # Parse the JSON string into a Python object to avoid double-encoding
                    plot_data = json.loads(fig.to_json())
                    
                    # Add display configuration to make it more user-friendly
                    plot_config = {
                        "displayModeBar": True,
                        "responsive": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"]
                    }
                    
                    # Return the processed data
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
                # Generate static image plot for a single parameter
                plot_buffer = plot_depth_vs_parameter(file_path, param)
                return StreamingResponse(plot_buffer, media_type="image/png")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error processing depth data: {str(e)}")
        print(f"Error details: {error_details}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ---------------- eDNA Analysis Endpoint ----------------
# Initialize the eDNA model once at startup
init_model(UPLOAD_FOLDER)

@app.post("/analyze/edna", 
          summary="Analyze eDNA Data",
          description="Upload eDNA sequence data and analyze for species detection")
async def analyze_edna_endpoint(file: UploadFile = File(...), force_train: bool = Query(False, description="Force retrain the model on this data")):
    """
    Analyze eDNA sequence data for species detection and invasive species alerts.
    
    The first upload will be used to train the model if no pre-trained model exists.
    """
    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get the current model
    clf, vectorizer = get_model()
    
    # Check if model is trained or force_train is requested
    if clf is None or vectorizer is None or force_train:
        # Try to train on the uploaded file
        if not train_new_model(file_path):
            return JSONResponse(
                status_code=500,
                content={"error": "Could not train or use eDNA model"}
            )
        
        # Get the updated model
        clf, vectorizer = get_model()
        
        # Analyze the data
        try:
            results = analyze_edna(file_path, clf, vectorizer)
            invasive = check_invasive(results, clf)
            
            # Format the invasive alert for better display
            if invasive:
                invasive_names = []
                for inv in invasive:
                    parts = inv.split('|')
                    if len(parts) > 2:
                        invasive_names.append(f"{parts[2]} ({parts[0]})")
                    else:
                        invasive_names.append(inv)
                        
                invasive_alert = f"ALERT: Found {len(invasive)} invasive species: {', '.join(invasive_names)}"
            else:
                invasive_alert = "None detected"
                
            return {
                "predicted_species": results,
                "invasive_alert": invasive_alert,
                "invasive_species": invasive,
                "note": "Model was trained on this file"
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Could not train or use eDNA model: {str(e)}"}
            )
    else:
        # Model already trained, just analyze
        try:
            results = analyze_edna(file_path, clf, vectorizer)
            invasive = check_invasive(results, clf)
            
            # Format the invasive alert for better display
            if invasive:
                invasive_names = []
                for inv in invasive:
                    parts = inv.split('|')
                    if len(parts) > 2:
                        invasive_names.append(f"{parts[2]} ({parts[0]})")
                    else:
                        invasive_names.append(inv)
                        
                invasive_alert = f"ALERT: Found {len(invasive)} invasive species: {', '.join(invasive_names)}"
            else:
                invasive_alert = "None detected"
                
            return {
                "predicted_species": results,
                "invasive_alert": invasive_alert,
                "invasive_species": invasive
            }
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Error analyzing eDNA: {str(e)}"}
            )

# ---------------- Fish Stock Analysis Endpoints ----------------
@app.get("/fish/forecast-chart", 
         summary="Get Interactive Fish Stock Forecast Chart",
         description="Returns a Plotly chart as JSON. A frontend can use this to render an interactive plot.")
def get_interactive_forecast_chart(
    use_default_data: bool = Query(True, description="Set to true to use sample data, false to use uploaded data")
):
    """
    Generates and returns the interactive Plotly forecast chart as a JSON object.
    
    Parameters:
    - use_default_data: Whether to use default data or previously uploaded data
    """
    if use_default_data:
        # Use sample data
        chart_json = generate_forecast_chart()
    else:
        # Try to use uploaded data if available
        fish_data_path = os.path.join(UPLOAD_FOLDER, "fish_stock_data.csv")
        if os.path.exists(fish_data_path):
            chart_json = generate_forecast_chart(fish_data_path)
        else:
            # Fallback to sample data
            chart_json = generate_forecast_chart()
    
    return JSONResponse(content=json.loads(chart_json), media_type="application/json")

@app.get("/fish/health-check",
         summary="Get Overfishing Status Chart",
         description="Returns a PNG image comparing total catch vs. stock per year.")
def get_health_check_chart(
    use_default_data: bool = Query(True, description="Set to true to use sample data, false to use uploaded data")
):
    """
    Generates and returns the overfishing health check chart as a static image.
    
    Parameters:
    - use_default_data: Whether to use default data or previously uploaded data
    """
    if use_default_data:
        # Use sample data
        image_bytes = generate_health_check_chart()
    else:
        # Try to use uploaded data if available
        fish_data_path = os.path.join(UPLOAD_FOLDER, "fish_stock_data.csv")
        if os.path.exists(fish_data_path):
            image_bytes = generate_health_check_chart(fish_data_path)
        else:
            # Fallback to sample data
            image_bytes = generate_health_check_chart()
    
    return StreamingResponse(image_bytes, media_type="image/png")

@app.get("/fish/sustainability-metrics",
         summary="Get Fish Stock Sustainability Metrics",
         description="Returns metrics about fish stock sustainability")
def get_sustainability_metrics(
    use_default_data: bool = Query(True, description="Set to true to use sample data, false to use uploaded data")
):
    """
    Calculates and returns metrics about fish stock sustainability.
    
    Parameters:
    - use_default_data: Whether to use default data or previously uploaded data
    """
    if use_default_data:
        # Use sample data
        metrics = calculate_sustainability_metrics()
    else:
        # Try to use uploaded data if available
        fish_data_path = os.path.join(UPLOAD_FOLDER, "fish_stock_data.csv")
        if os.path.exists(fish_data_path):
            metrics = calculate_sustainability_metrics(fish_data_path)
        else:
            # Fallback to sample data
            metrics = calculate_sustainability_metrics()
    
    return metrics

@app.post("/fish/upload-data",
          summary="Upload Fish Stock Data",
          description="Upload a CSV file with fish stock data")
async def upload_fish_data(file: UploadFile = File(...)):
    """
    Upload a CSV file with fish stock data.
    
    The file should contain at least these columns:
    - Year: Year or date 
    - Stock: Total fish stock
    - TotalCatch: Amount of fish caught
    
    Returns:
        Status message about the upload
    """
    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, "fish_stock_data.csv")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate the file
        try:
            df = pd.read_csv(file_path)
            required_columns = ['Year', 'Stock', 'TotalCatch']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Missing required columns: {', '.join(missing_columns)}"}
                )
            
            return {"message": "Fish stock data uploaded successfully", "filename": file.filename}
        
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid CSV file: {str(e)}"}
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error uploading file: {str(e)}"}
        )

# ---------------- Fish Classification Endpoint ----------------
@app.post("/classify/fish",
          summary="Classify a Fish Image",
          description="Upload an image of a fish to classify it into one of the supported species.")
async def classify_fish(file: UploadFile = File(...)):
    """
    Classify a fish image.
    
    Supported species are:
    - Black Sea Sprat
    - Gilt-Head Bream
    - Hourse Mackerel
    - Red Mullet
    - Red Sea Bream
    - Sea Bass
    - Shrimp
    - Striped Red Mullet
    - Trout
    """
    try:
        # Save the uploaded file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Predict the class of the image
        predicted_class, confidence = predict_image(file_path)
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error classifying image: {str(e)}"}
        )
