# Ocean AI Interactive Visualizations

This repository contains a backend API and frontend example for creating interactive ocean data visualizations.

## Features

- **Interactive Forecast Visualizations**: Create and view interactive time series forecasts of sea surface temperature (SST) data.
- **Interactive Depth Profile Analysis**: Analyze and visualize depth vs. parameters (chlorophyll, pH, salinity) relationships.
- **eDNA Analysis**: Upload and analyze environmental DNA sequences to detect species and identify invasive species.
- **Support for both interactive and static visualizations**: API endpoints can return either Plotly JSON for interactive visualizations or static PNG images.

## Backend API

The backend is built with FastAPI and offers the following endpoints:

### Visualization Endpoints

1. `POST /visualize/forecast`
   - Generates SST forecast visualizations
   - Parameters:
     - `files` (optional): Time series data files to upload
     - `date_col` (optional): Date column name
     - `target_col` (optional): Target column name
     - `future_days` (optional, default=30): Number of days to forecast
     - `use_default_data` (optional, default=false): Whether to use default dataset
     - `format` (optional, default="interactive"): Output format - "interactive" or "image"

2. `POST /visualize/depth`
   - Generates depth profile visualizations
   - Parameters:
     - `file` (optional): Depth data file to upload
     - `parameter` (optional, default="chlorophyll"): Parameter to plot
     - `use_default_data` (optional, default=false): Whether to use default dataset
     - `format` (optional, default="interactive"): Output format - "interactive" or "image"

### Analysis Endpoints

1. `POST /analyze/edna`
   - Analyzes eDNA sequence data for species detection
   - Parameters:
     - `file`: FASTA file containing DNA sequences

## Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- Plotly
- Prophet
- pandas
- scikit-learn
- matplotlib
- Biopython (for eDNA analysis)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ocean-ai-prototype.git
   cd ocean-ai-prototype
   ```

2. Install dependencies:
   ```
   pip install -r backend/requirements.txt
   ```

3. Run the backend server:
   ```
   cd backend
   python run_server.py
   ```

4. Open the frontend example in a web browser:
   ```
   cd ../frontend-example
   # Use a local web server or simply open index.html in a browser
   ```

## Using the Frontend Example

The frontend example demonstrates how to create interactive visualizations using the API:

1. **Sea Surface Temperature Forecast**:
   - Select forecast days and data source
   - Click "Generate Forecast" to create an interactive forecast visualization
   - Use the Plotly controls to zoom, pan, and explore the forecast

2. **Depth Profile Analysis**:
   - Select parameter (chlorophyll, pH, or salinity)
   - Choose data source
   - Click "Generate Depth Profile" to create an interactive depth profile

## API Integration

To integrate the API into your own application:

1. Make a POST request to the appropriate endpoint
2. For interactive visualizations, set `format=interactive`
3. Parse the returned JSON and use Plotly to render the visualization:
   ```javascript
   fetch('http://localhost:8000/visualize/forecast', {
       method: 'POST',
       body: formData // Include parameters like format=interactive
   })
   .then(response => response.json())
   .then(plotlyJson => {
       Plotly.newPlot('your-div-id', plotlyJson.data, plotlyJson.layout);
   });
   ```

## CORS Support

To enable cross-origin requests in a production environment, update the FastAPI app in `main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## License

This project is licensed under the MIT License.
