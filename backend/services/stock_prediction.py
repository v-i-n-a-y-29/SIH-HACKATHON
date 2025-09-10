"""
Stock prediction service for fish stocks analysis.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from prophet import Prophet
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import json
import os

# Suppress informational messages from Prophet
import logging
logging.getLogger('prophet').setLevel(logging.ERROR)
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)

def load_or_create_sample_data(file_path=None):
    """
    Load fish stock data from a CSV file, or create sample data if file doesn't exist.
    
    Args:
        file_path: Path to CSV file containing Year, Stock, TotalCatch columns
        
    Returns:
        Pandas DataFrame with fish stock data
    """
    if file_path and os.path.exists(file_path):
        return pd.read_csv(file_path)
    
    # Create sample data for demonstration purposes
    years = [f"201{i}-01-01" for i in range(0, 10)]
    stock = [15000, 14500, 14000, 13700, 13400, 13100, 12800, 12500, 12200, 11900]
    catch = [12000, 11800, 11600, 11400, 11200, 11000, 10800, 10600, 10400, 10200]
    
    df = pd.DataFrame({
        'Year': years,
        'Stock': stock,
        'TotalCatch': catch
    })
    return df

def generate_forecast_chart(file_path=None):
    """
    Generates an interactive stock forecast chart using Prophet and Plotly.
    
    Args:
        file_path: Path to CSV file containing fish stock data
        
    Returns:
        Plotly chart as JSON string
    """
    df = load_or_create_sample_data(file_path)
    
    # Prepare data for Prophet
    df_prophet = df[['Year', 'Stock']].copy()
    
    # Format dates if needed
    if not pd.to_datetime(df_prophet['Year'], errors='coerce').isna().any():
        df_prophet['Year'] = pd.to_datetime(df_prophet['Year'])
    else:
        # Handle year-only format
        df_prophet['Year'] = df_prophet['Year'].apply(lambda x: x.split('-')[0] if '-' in str(x) else x)
        df_prophet['Year'] = pd.to_datetime(df_prophet['Year'], format='%Y', errors='coerce')
    
    df_prophet.rename(columns={'Year': 'ds', 'Stock': 'y'}, inplace=True)

    # Train the model
    model = Prophet()
    model.fit(df_prophet)

    # Make a 5-year future dataframe
    future = model.make_future_dataframe(periods=5, freq='Y')
    forecast = model.predict(future)

    # Create an interactive Plotly figure
    fig = go.Figure()

    # Add the lower and upper forecast bounds (the shaded area)
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper'],
        fill=None, mode='lines', line_color='rgba(0,100,80,0.2)', name='Upper Bound'
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower'],
        fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)', name='Lower Bound'
    ))
    
    # Add the main forecast line
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines', line=dict(color='blue', width=4), name='Forecast'
    ))
    
    # Add the actual historical data points
    fig.add_trace(go.Scatter(
        x=df_prophet['ds'], y=df_prophet['y'],
        mode='markers', marker=dict(color='black', size=8), name='Actual Stock'
    ))

    fig.update_layout(
        title='Interactive Fish Stock 5-Year Forecast 🔮',
        xaxis_title='Year',
        yaxis_title='Stock Quantity',
        legend_title='Legend',
        template='plotly_white'
    )
    
    # Return the figure as a JSON object
    return fig.to_json()

def generate_health_check_chart(file_path=None):
    """
    Generates the overfishing status chart with a detailed legend.
    
    Args:
        file_path: Path to CSV file containing fish stock data
        
    Returns:
        BytesIO object containing PNG image
    """
    df = load_or_create_sample_data(file_path)
    
    # Handle date formatting if needed
    if 'Year' in df.columns:
        if isinstance(df['Year'].iloc[0], str) and '-' in df['Year'].iloc[0]:
            df['Year'] = df['Year'].apply(lambda x: x.split('-')[0])

    plt.figure(figsize=(12, 7))
    bar_width = 0.4
    index = pd.Index(range(len(df['Year'])))

    colors = ['red' if df['TotalCatch'].iloc[i] > 0.8 * df['Stock'].iloc[i] else 'green' for i in range(len(df))]

    stock_bar = plt.bar(index, df['Stock'], bar_width, label='Total Stock', color='skyblue')
    plt.bar(index + bar_width, df['TotalCatch'], bar_width, color=colors)
    
    red_patch = mpatches.Patch(color='red', label='Overfishing Alert (>80%)')
    green_patch = mpatches.Patch(color='green', label='Safe (<80%)')
    
    plt.legend(handles=[stock_bar, red_patch, green_patch])

    plt.xlabel('Year')
    plt.ylabel('Quantity')
    plt.title('Overfishing Status: Health Check 🩺')
    plt.xticks(index + bar_width / 2, df['Year'], rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

def calculate_sustainability_metrics(file_path=None):
    """
    Calculate sustainability metrics from fish stock data.
    
    Args:
        file_path: Path to CSV file containing fish stock data
        
    Returns:
        Dictionary with sustainability metrics
    """
    df = load_or_create_sample_data(file_path)
    
    # Calculate metrics
    current_stock = df['Stock'].iloc[-1]
    previous_stock = df['Stock'].iloc[-2] if len(df) > 1 else df['Stock'].iloc[-1]
    stock_change_percent = ((current_stock - previous_stock) / previous_stock) * 100
    
    current_catch = df['TotalCatch'].iloc[-1]
    exploitation_rate = (current_catch / current_stock) * 100
    
    # Sustainability status
    if exploitation_rate > 80:
        status = "Overfishing"
        recommendation = "Reduce fishing effort by at least 30%"
    elif exploitation_rate > 60:
        status = "Fully Exploited"
        recommendation = "Maintain current fishing levels"
    else:
        status = "Sustainable"
        recommendation = "Stock is healthy, can maintain current fishing levels"
    
    # Calculate future trend based on the last 3 years
    recent_df = df.tail(3)
    if len(recent_df) >= 3:
        trend_direction = "Increasing" if recent_df['Stock'].iloc[-1] > recent_df['Stock'].iloc[-3] else "Decreasing"
    else:
        trend_direction = "Stable"
    
    # Return metrics
    return {
        "current_stock": int(current_stock),
        "stock_change_percent": round(stock_change_percent, 2),
        "exploitation_rate": round(exploitation_rate, 2),
        "sustainability_status": status,
        "recommendation": recommendation,
        "trend": trend_direction
    }
