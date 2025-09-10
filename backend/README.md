# 🌊 Ocean AI Prototype

A comprehensive Ocean AI analysis platform with fish classification, eDNA analysis, and ocean data forecasting.

## ✨ Features

- 🐟 **Fish Classification**: AI-powered fish species identification from images (29 species supported)
- 🧬 **eDNA Analysis**: Environmental DNA sequence analysis for species detection
- 📈 **Fish Stock Prediction**: Time series forecasting for sustainable fishing
- 🌊 **Ocean Data Analysis**: Depth profile visualization and parameter analysis

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Server
```bash
# Option 1: Direct uvicorn command
python -m uvicorn app.main:app --reload

# Option 2: Using the run script
python run_server.py
```

The server will start at: http://127.0.0.1:8000

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Root endpoint**: http://127.0.0.1:8000/

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── fish.py          # Fish classification & stock endpoints
│   │   │   ├── edna.py          # eDNA analysis endpoints  
│   │   │   ├── forecast.py      # Ocean forecasting endpoints
│   │   │   └── ocean_data.py    # Ocean data analysis endpoints
│   │   └── api_v1.py
│   ├── core/
│   │   ├── config.py            # Configuration settings
│   │   └── routes.py            # Route configuration
│   ├── models/
│   │   ├── fish_classification/ # Fish classification model
│   │   └── edna/               # eDNA model storage
│   ├── services/
│   │   ├── fish_classification.py
│   │   ├── stock_prediction.py
│   │   ├── forecast.py
│   │   └── edna_analysis.py
│   └── main.py                  # FastAPI application
├── data/                        # Data files
├── requirements.txt
└── run_server.py               # Server startup script
```

## 🔬 API Endpoints

### Fish Analysis
- `POST /api/v1/fish/classify` - Classify fish from image
- `GET /api/v1/fish/stock/forecast` - Get stock forecast
- `GET /api/v1/fish/stock/health` - Get stock health metrics
- `GET /api/v1/fish/stock/metrics` - Get sustainability metrics

### eDNA Analysis  
- `POST /api/v1/edna/analyze` - Analyze eDNA sequences

### Ocean Forecasting
- `POST /api/v1/forecast/` - Generate time series forecasts

### Ocean Data
- `POST /api/v1/ocean/depth-profile` - Generate depth profile visualizations

## 🎯 Usage Examples

### Fish Classification
Upload an image of a fish to get species identification with confidence score.

### eDNA Analysis
Upload FASTA sequences to detect species and identify invasive species.

### Stock Prediction
Get interactive forecasts and sustainability metrics for fish populations.

### Ocean Data Analysis
Visualize depth profiles for parameters like chlorophyll, pH, and salinity.

## 🔧 Configuration

The application configuration is managed in `app/core/config.py`. Key settings include:
- Data directory paths
- Model file locations  
- API settings

## 📝 Notes

- The fish classification model supports 29 different fish species
- All endpoints return JSON responses
- Interactive Plotly visualizations are available for most analysis endpoints
- The server includes CORS middleware for frontend integration
