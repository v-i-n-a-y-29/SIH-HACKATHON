# Fish Stock Analysis Module

This module adds fish stock prediction and sustainability analysis to the Ocean AI API.

## Features

1. **Interactive Fish Stock Forecast Chart**: 
   - Visualize and predict fish stock levels for the next 5 years
   - Uses Prophet time series forecasting

2. **Overfishing Status Chart**:
   - Visual comparison of total catch vs. available stock
   - Color-coded to highlight overfishing risks

3. **Sustainability Metrics**:
   - Calculate key sustainability indicators
   - Get recommendations based on current exploitation rates

## Endpoints

### 1. Get Interactive Forecast Chart
```
GET /fish/forecast-chart
```
Returns a Plotly chart as JSON that can be rendered in any frontend

### 2. Get Overfishing Status Chart
```
GET /fish/health-check
```
Returns a PNG image comparing total catch vs. stock per year

### 3. Get Sustainability Metrics
```
GET /fish/sustainability-metrics
```
Returns key metrics about fish stock sustainability

### 4. Upload Fish Stock Data
```
POST /fish/upload-data
```
Upload custom fish stock data in CSV format

## Data Format

Fish stock data should be in CSV format with the following columns:
- `Year`: Year or date in YYYY-MM-DD format
- `Stock`: Total fish stock quantity
- `TotalCatch`: Amount of fish caught

## Integration with Ocean AI

This module is fully integrated with the existing Ocean AI platform, allowing users to:
- Compare ocean parameter data with fish stock trends
- Analyze the relationship between environmental factors and fish populations
- Make data-driven decisions for sustainable fishing practices
