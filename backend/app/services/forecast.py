# backend/services/forecast.py
import pandas as pd
import numpy as np
import math
from sklearn.metrics import mean_absolute_error, mean_squared_error
# Set Matplotlib backend to non-GUI 'Agg' to avoid Tkinter errors
import matplotlib
matplotlib.use('Agg')  # This must be done before importing pyplot
import matplotlib.pyplot as plt
from prophet import Prophet  # ensure prophet is installed
import os
import io
import traceback
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_date_and_target(df):
    # Detect date column
    date_candidates = [c for c in df.columns if any(k in c.lower() for k in ("date","time","timestamp"))]
    date_col = date_candidates[0] if date_candidates else None
    if date_col is None:
        # fallback: try parsing first column to datetime
        for c in df.columns:
            s = pd.to_datetime(df[c], errors='coerce')
            if s.notna().sum() >= max(10, int(0.2*len(df))):
                date_col = c
                break
    # Detect numeric target column
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # prefer names
    pref = ["stock_value","value","sea_surface_temp","sst","salinity","chlorophyll","catch","biomass"]
    target_col = None
    for p in pref:
        for c in df.columns:
            if p in c.lower():
                target_col = c
                break
        if target_col:
            break
    if target_col is None:
        if numeric_cols:
            # select numeric column with most non-nulls
            counts = {c: df[c].notna().sum() for c in numeric_cols}
            target_col = max(counts, key=counts.get)
    return date_col, target_col

def prepare_df(file_path, date_col=None, target_col=None):
    df = pd.read_csv(file_path)
    if date_col is None or target_col is None:
        date_col, target_col = detect_date_and_target(df)
        if date_col is None or target_col is None:
            raise ValueError("Could not auto-detect date or target column. Provide date_col/target_col.")
    df2 = df[[date_col, target_col]].copy()
    df2.rename(columns={date_col: "ds", target_col: "y"}, inplace=True)
    # Coerce types
    df2['ds'] = pd.to_datetime(df2['ds'], errors='coerce')
    df2['y'] = pd.to_numeric(df2['y'], errors='coerce')
    # Drop missing and sort
    df2 = df2.dropna(subset=['ds','y']).sort_values('ds').reset_index(drop=True)
    # Collapse duplicate timestamps by mean
    if df2['ds'].duplicated().any():
        df2 = df2.groupby('ds', as_index=False).mean()
    # Try to infer frequency for Prophet
    try:
        inferred = pd.infer_freq(df2['ds'])
    except Exception:
        inferred = None
    df2.attrs['inferred_freq'] = inferred
    return df2

def plot_depth_vs_parameter(regressor_file_path, parameter_name="Chlorophyl", save_path=None):
    """Generate a plot showing the relationship between depth and a selected parameter."""
    try:
        import matplotlib.pyplot as plt
        
        # Read the regressor file
        df_reg = pd.read_csv(regressor_file_path)
        
        # Clean column names
        df_reg.columns = [str(c).replace('.','_').replace(' ','_') for c in df_reg.columns]
        
        # Sort by depth for a clearer plot
        df_reg = df_reg.sort_values('Depth')
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.scatter(df_reg['Depth'], df_reg[parameter_name], alpha=0.7)
        plt.plot(df_reg['Depth'], df_reg[parameter_name], alpha=0.4)
        
        plt.title(f'Depth vs {parameter_name}')
        plt.xlabel('Depth (m)')
        plt.ylabel(parameter_name)
        plt.grid(True, alpha=0.3)
        
        # Set y-axis to start at 0 if all values are positive
        if df_reg[parameter_name].min() >= 0:
            plt.ylim(bottom=0)
        
        # Invert y-axis for depth (depth increases downward)
        plt.gca().invert_yaxis()
        
        if save_path:
            # Save the plot to a file
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
            print(f"Depth vs {parameter_name} plot saved to {save_path}")
            return os.path.abspath(save_path)
        else:
            # Save plot to a memory buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return buf
    
    except Exception as e:
        print(f"Error creating depth vs parameter plot: {str(e)}")
        return None

def plot_combined_depth_parameters(file_path, save_path=None):
    """
    Generate a combined plot showing depth vs chlorophyll, pH, and salinity on the same graph
    with multiple axes, similar to the Marine Insights dashboard.
    
    Args:
        file_path (str): Path to the CSV file with depth data
        save_path (str, optional): Path to save the plot
        
    Returns:
        BytesIO object or path to the saved plot
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        
        # Read the regressor file
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = [str(c).replace('.','_').replace(' ','_') for c in df.columns]
        
        # Sort by depth for a clearer plot
        df = df.sort_values('Depth')
        
        # Create the figure with a dark blue background
        plt.figure(figsize=(12, 6), facecolor='#1a3a5f')
        ax1 = plt.gca()
        ax1.set_facecolor('#1a3a5f')
        
        # Create additional y-axes for multiple parameters
        ax2 = ax1.twinx()
        ax3 = ax1.twinx()
        
        # Offset the right axes to prevent overlap
        ax3.spines['right'].set_position(('outward', 60))
        
        # Plot the data with distinct colors
        chlorophyll_line, = ax1.plot(df['Depth'], df['Chlorophyl'], 'g-', linewidth=2, label='Chlorophyll')
        ph_line, = ax2.plot(df['Depth'], df['pH'], 'y-', linewidth=2, label='pH Level')
        salinity_line, = ax3.plot(df['Depth'], df['Salinity'], 'r-', linewidth=2, label='Salinity')
        
        # Set labels and title with light colors for dark background
        ax1.set_xlabel('Depth (m)', color='white')
        ax1.set_ylabel('Chlorophyll (mg/m³)', color='#98fb98')  # Light green
        ax2.set_ylabel('pH Level', color='#ffff99')  # Light yellow
        ax3.set_ylabel('Salinity (PSU)', color='#ff9999')  # Light red
        
        # Set title with light color
        plt.title('Ocean Parameters vs Depth', color='white', fontsize=16)
        
        # Customize axis colors to match the lines
        ax1.tick_params(axis='y', colors='#98fb98')
        ax2.tick_params(axis='y', colors='#ffff99')
        ax3.tick_params(axis='y', colors='#ff9999')
        ax1.tick_params(axis='x', colors='white')
        
        # Add grid with subtle lines
        ax1.grid(True, alpha=0.2, color='white')
        
        # Customize spines to match dark theme
        for ax in [ax1, ax2, ax3]:
            for spine in ax.spines.values():
                spine.set_color('#456789')
        
        # Create a combined legend
        lines = [chlorophyll_line, ph_line, salinity_line]
        labels = [line.get_label() for line in lines]
        plt.legend(lines, labels, loc='upper right', framealpha=0.8, facecolor='#1a3a5f', edgecolor='#456789', labelcolor='white')
        
        # Invert y-axis for depth (depth increases downward)
        ax1.invert_yaxis()
        
        # Adjust layout
        plt.tight_layout()
        
        if save_path:
            # Save the plot to a file
            plt.savefig(save_path, facecolor='#1a3a5f', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Combined depth plot saved to {save_path}")
            return os.path.abspath(save_path)
        else:
            # Save plot to a memory buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', facecolor='#1a3a5f', dpi=300, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            return buf
    
    except Exception as e:
        print(f"Error creating combined depth plot: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def plot_combined_depth_parameters_plotly(file_path):
    """
    Generate an interactive combined plot with Plotly showing depth vs chlorophyll, pH, and salinity 
    with multiple parameters on the same graph.
    
    Args:
        file_path (str): Path to the CSV file with depth data
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Read the data
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = [str(c).replace('.','_').replace(' ','_') for c in df.columns]
        
        # Sort by depth for a clearer plot
        df = df.sort_values('Depth')
        
        # Create a figure with secondary y-axes
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces for each parameter
        fig.add_trace(
            go.Scatter(
                x=df['Depth'],
                y=df['Chlorophyl'],
                name="Chlorophyll",
                line=dict(color="#7CFC00", width=3),
                hovertemplate="Depth: %{x}m<br>Chlorophyll: %{y} mg/m³"
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['Depth'],
                y=df['pH'],
                name="pH Level",
                line=dict(color="#FFFF00", width=3),
                hovertemplate="Depth: %{x}m<br>pH: %{y}"
            ),
            secondary_y=True,
        )
        
        # Add salinity trace
        fig.add_trace(
            go.Scatter(
                x=df['Depth'],
                y=df['Salinity'],
                name="Salinity",
                line=dict(color="#FF6347", width=3),
                hovertemplate="Depth: %{x}m<br>Salinity: %{y} PSU",
                visible='legendonly'  # Initially hidden, can be toggled
            ),
            secondary_y=True,
        )
        
        # Customize appearance
        fig.update_layout(
            title="Ocean Parameters vs Depth",
            title_font=dict(size=24, color="#FFFFFF"),
            legend=dict(
                font=dict(color="#FFFFFF"),
                bgcolor="rgba(26, 58, 95, 0.8)"
            ),
            paper_bgcolor="#1a3a5f",
            plot_bgcolor="#1a3a5f",
            font=dict(color="#FFFFFF"),
            hovermode="closest",
            margin=dict(l=80, r=80, t=100, b=80),
            xaxis=dict(
                title="Depth (m)",
                color="#FFFFFF",
                gridcolor="rgba(255, 255, 255, 0.2)",
                zerolinecolor="rgba(255, 255, 255, 0.5)"
            ),
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text="Chlorophyll (mg/m³)",
            title_font=dict(color="#7CFC00"),
            tickfont=dict(color="#7CFC00"),
            gridcolor="rgba(255, 255, 255, 0.2)",
            secondary_y=False
        )
        
        fig.update_yaxes(
            title_text="pH / Salinity",
            title_font=dict(color="#FFFF00"),
            tickfont=dict(color="#FFFF00"),
            gridcolor="rgba(255, 255, 255, 0.1)",
            secondary_y=True
        )
        
        # Invert x-axis to show depth increasing to the right
        fig.update_xaxes(autorange="reversed")
        
        # Add helpful annotations
        fig.add_annotation(
            x=0.5,
            y=1.15,
            xref="paper",
            yref="paper",
            text="Interactive Ocean Data Visualization",
            showarrow=False,
            font=dict(size=14, color="#FFFFFF"),
            align="center",
            opacity=0.7
        )
        
        # Add buttons for data toggles
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    buttons=[
                        dict(
                            args=[{"visible": [True, True, True]}],
                            label="Show All",
                            method="update"
                        ),
                        dict(
                            args=[{"visible": [True, True, False]}],
                            label="Chlorophyll & pH",
                            method="update"
                        ),
                        dict(
                            args=[{"visible": [True, False, True]}],
                            label="Chlorophyll & Salinity",
                            method="update"
                        )
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top",
                    bgcolor="rgba(26, 58, 95, 0.8)",
                    font=dict(color="#FFFFFF")
                )
            ]
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating interactive combined depth plot: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def plot_depth_vs_parameter_plotly(file_path, parameter):
    """
    Generate an interactive Plotly plot for depth vs a specific parameter.
    
    Args:
        file_path (str): Path to the CSV file with depth data
        parameter (str): Parameter to plot against depth (e.g. 'Chlorophyl', 'pH', 'Salinity')
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object
    """
    try:
        import plotly.graph_objects as go
        
        # Read the data
        df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = [str(c).replace('.','_').replace(' ','_') for c in df.columns]
        
        # Sort by depth for a clearer plot
        df = df.sort_values('Depth')
        
        # Set colors based on parameter
        colors = {
            'Chlorophyl': '#7CFC00',  # Bright green
            'pH': '#FFFF00',         # Yellow
            'Salinity': '#FF6347'     # Tomato red
        }
        color = colors.get(parameter, '#1E90FF')  # Default to dodger blue
        
        # Set units based on parameter
        units = {
            'Chlorophyl': 'mg/m³',
            'pH': '',
            'Salinity': 'PSU'
        }
        unit = units.get(parameter, '')
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=df['Depth'],
                y=df[parameter],
                mode='lines+markers',
                name=parameter,
                line=dict(color=color, width=3),
                marker=dict(size=8, color=color),
                hovertemplate=f"Depth: %{{x}}m<br>{parameter}: %{{y}}{unit}"
            )
        )
        
        # Customize appearance
        fig.update_layout(
            title=f"{parameter} vs Depth",
            title_font=dict(size=24, color="#FFFFFF"),
            paper_bgcolor="#1a3a5f",
            plot_bgcolor="#1a3a5f",
            font=dict(color="#FFFFFF"),
            hovermode="closest",
            xaxis=dict(
                title="Depth (m)",
                color="#FFFFFF",
                gridcolor="rgba(255, 255, 255, 0.2)",
                zerolinecolor="rgba(255, 255, 255, 0.5)"
            ),
            yaxis=dict(
                title=f"{parameter} {unit}",
                color=color,
                gridcolor="rgba(255, 255, 255, 0.2)",
                zerolinecolor="rgba(255, 255, 255, 0.5)"
            ),
            margin=dict(l=80, r=80, t=100, b=80)
        )
        
        # Invert x-axis to show depth increasing to the right
        fig.update_xaxes(autorange="reversed")
        
        # Add hover information
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="#1a3a5f",
                font_size=14,
                font_family="Arial"
            )
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating Plotly depth vs {parameter} plot: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def create_future_forecast_plot(historical_df, forecast_df, target_col=None):
    """
    Creates a visualization that clearly shows both historical data and future forecasts.
    
    Args:
        historical_df (pd.DataFrame): DataFrame with historical data ('ds', 'y').
        forecast_df (pd.DataFrame): DataFrame with forecast data from Prophet ('ds', 'yhat', 'yhat_lower', 'yhat_upper').
        target_col (str, optional): The name of the target variable being forecast.
        
    Returns:
        BytesIO: A buffer containing the PNG image of the forecast plot.
    """
    try:
        # Set up the figure and axes
        plt.figure(figsize=(12, 7))
        
        # Get the date where historical data ends and forecast begins
        historical_end = historical_df['ds'].iloc[-1]
        
        # Separate the forecast into historical period and future period
        historical_forecast = forecast_df[forecast_df['ds'] <= historical_end]
        future_forecast = forecast_df[forecast_df['ds'] > historical_end]
        
        # Determine the target column name for the plot
        if target_col is None or target_col == "":
            target_col = "Sea Surface Temperature (°C)"
        
        # Plot historical actual data
        plt.plot(historical_df['ds'], historical_df['y'], 'b-', 
                 label='Historical Data', linewidth=2)
        
        # Plot the forecast over the historical period (in-sample fit)
        plt.plot(historical_forecast['ds'], historical_forecast['yhat'], 'r--', 
                 label='Model Fit', linewidth=2, alpha=0.7)
        
        # Plot the future forecast
        plt.plot(future_forecast['ds'], future_forecast['yhat'], 'r-', 
                 label='Future Forecast', linewidth=3)
        
        # Add uncertainty intervals for the future forecast
        plt.fill_between(future_forecast['ds'], 
                        future_forecast['yhat_lower'], 
                        future_forecast['yhat_upper'], 
                        color='r', alpha=0.2, label='95% Confidence Interval')
        
        # Add a vertical line to separate historical data from future predictions
        plt.axvline(x=historical_end, color='k', linestyle='--', label='Present', alpha=0.7)
        
        # Add labels and title
        plt.xlabel('Date')
        plt.ylabel(target_col)
        plt.title(f'Historical Data and Future Forecast for {target_col}')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
        
        # Format the x-axis to show dates nicely
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the figure to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close()
        buf.seek(0)
        
        return buf
        
    except Exception as e:
        logger.error(f"Error creating future forecast plot: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_depth_plots(file_path, save_dir=None):
    """
    Generates plots for depth vs. Chlorophyll, pH, and Salinity.
    
    Args:
        file_path (str): Path to the CSV file with depth data.
        save_dir (str): Directory to save the plots.
        
    Returns:
        dict: A dictionary containing paths to the generated plots.
    """
    depth_plots = {}
    # Generate plots for chlorophyll, pH, and salinity
    for param in ["Chlorophyl", "pH", "Salinity"]:
        if save_dir:
            save_path = os.path.join(save_dir, f"depth_vs_{param.lower()}.png")
            plot_path = plot_depth_vs_parameter(file_path, param, save_path)
        else:
            plot_path = plot_depth_vs_parameter(file_path, param)
            
        if plot_path:
            depth_plots[param] = plot_path
    
    # Generate combined plot
    if save_dir:
        combined_save_path = os.path.join(save_dir, "depth_combined_parameters.png")
        combined_plot = plot_combined_depth_parameters(file_path, combined_save_path)
    else:
        combined_plot = plot_combined_depth_parameters(file_path)
    
    if combined_plot:
        depth_plots["combined"] = combined_plot
        
    return depth_plots

def run_prophet(file_path, regressor_file_path=None, date_col=None, target_col=None, test_frac=0.2, future_periods=30, save_csv_path="prophet_forecast_output.csv", save_plots=True):
    df_p = prepare_df(file_path, date_col, target_col)
    
    # Handle regressors
    regressor_names = []
    if regressor_file_path:
        print(f"Loading regressor data from: {regressor_file_path}")
        try:
            df_reg = pd.read_csv(regressor_file_path)
            print(f"Regressor file columns: {df_reg.columns.tolist()}")
            
            # Clean up regressor column names
            df_reg.columns = [str(c).replace('.','_').replace(' ','_') for c in df_reg.columns]
            print(f"Cleaned regressor columns: {df_reg.columns.tolist()}")
            
            # For datasets like MergedData.csv that don't have dates but have depth measurements,
            # we'll use a different approach - we'll select representative samples and add them
            # as extra features rather than trying to merge by date
            
            # Select a subset of representative rows
            # Sort by depth to ensure we're getting a good distribution
            df_reg = df_reg.sort_values('Depth').copy()
            
            # Select samples at regular intervals
            n_samples = min(20, len(df_reg))  # Take at most 20 samples
            sample_indices = np.linspace(0, len(df_reg) - 1, n_samples).astype(int)
            df_reg_samples = df_reg.iloc[sample_indices]
            
            print(f"Selected {len(df_reg_samples)} representative samples from regressor file")
            
            # Calculate mean values for each parameter to use as regressor features
            mean_salinity = df_reg['Salinity'].mean()
            mean_ph = df_reg['pH'].mean()
            mean_chlorophyl = df_reg['Chlorophyl'].mean()
            
            # Add these as constants to our main dataframe
            df_p['mean_salinity'] = mean_salinity
            df_p['mean_ph'] = mean_ph
            df_p['mean_chlorophyl'] = mean_chlorophyl
            
            print(f"Added average values from regressor data as constant features:")
            print(f"  - mean_salinity: {mean_salinity:.2f}")
            print(f"  - mean_ph: {mean_ph:.2f}")
            print(f"  - mean_chlorophyl: {mean_chlorophyl:.6f}")
            
            # Get the names of regressor columns we just added
            regressor_names = ['mean_salinity', 'mean_ph', 'mean_chlorophyl']
            print(f"Using regressors: {regressor_names}")
            
            # No need to drop NaN rows since we added constants
            print(f"Final dataframe shape for modeling: {df_p.shape}")
            
        except Exception as e:
            import traceback
            print(f"Error processing regressor file: {str(e)}")
            print(traceback.format_exc())
            # Continue without regressors if there's an error
            regressor_names = []

    n = len(df_p)
    # Guard for tiny datasets
    n_test = max(1, int(n * test_frac)) if n > 5 else max(1, int(max(1, n//5)))
    train_df = df_p.iloc[:-n_test].copy() if n_test < n else df_p.iloc[: max(1, n-1)].copy()
    test_df = df_p.iloc[-n_test:].copy() if n_test < n else df_p.iloc[-1:].copy()
    
    # Fit
    # Configure Prophet seasonalities based on data span
    try:
        span_days = (df_p['ds'].max() - df_p['ds'].min()).days
    except Exception:
        span_days = None
    # If we have < ~180-270 days, yearly seasonality is not learnable; prefer weekly
    use_yearly = span_days is not None and span_days >= 270
    use_weekly = not use_yearly  # enable weekly for short histories

    m = Prophet(
        yearly_seasonality=use_yearly,
        weekly_seasonality=use_weekly,
        daily_seasonality=False,
        seasonality_mode="additive"
    )
    for name in regressor_names:
        m.add_regressor(name)
    m.fit(train_df)
    
    # Create future to cover test horizon
    # Use inferred frequency if available; default to 'D'
    freq = df_p.attrs.get('inferred_freq') or 'D'
    future = m.make_future_dataframe(periods=n_test, freq=freq)
    if regressor_names:
        # For constant features from MergedData, just add them to future dataframe
        for name in regressor_names:
            future[name] = df_p[name].iloc[0]  # Use the same constant value for all future dates
        print(f"Added regressor values to future dataframe with shape {future.shape}")

    forecast = m.predict(future)
    
    # Align predictions to test set
    pred = forecast[['ds','yhat']].merge(test_df[['ds','y']], on='ds', how='inner')
    if pred.empty:
        # fallback align by tails
        pred = forecast[['ds','yhat']].tail(n_test).copy()
        pred['y'] = test_df['y'].values[-len(pred):]

    mae = mean_absolute_error(pred['y'], pred['yhat'])
    rmse = math.sqrt(mean_squared_error(pred['y'], pred['yhat']))
    
    # Fit on full data and forecast future_periods
    m_full = Prophet(
        yearly_seasonality=use_yearly,
        weekly_seasonality=use_weekly,
        daily_seasonality=False,
        seasonality_mode="additive"
    )
    for name in regressor_names:
        m_full.add_regressor(name)
    m_full.fit(df_p)
    
    # Increase future periods to show more future forecast trends
    future_full = m_full.make_future_dataframe(periods=future_periods, freq=freq)
    if regressor_names:
        # Add the same constant regressor values to future periods
        for name in regressor_names:
            future_full[name] = df_p[name].iloc[0]  # Use the same constant value
        print(f"Added regressor values to full future dataframe with shape {future_full.shape}")

    forecast_full = m_full.predict(future_full)
    
    # Save last future_periods to CSV
    forecast_to_save = forecast_full[['ds','yhat','yhat_lower','yhat_upper']].tail(future_periods).copy()
    forecast_to_save.to_csv(save_csv_path, index=False)
    
    # Create an enhanced future forecast visualization
    future_forecast_plot = create_future_forecast_plot(df_p, forecast_full, 
                                                      target_col if target_col else detect_date_and_target(pd.read_csv(file_path))[1])
    
    # Initialize results dictionary
    results = {
        "mae": mae,
        "rmse": rmse,
        "forecast_csv": os.path.abspath(save_csv_path),
        "forecast_full_tail": forecast_to_save,
        "historical_df": df_p,  # Include historical data for interactive plotting
        # Diagnostics to explain divergence
        "diagnostics": {
            "n_observations": int(n),
            "test_points": int(len(test_df)),
            "inferred_freq": freq,
            "target_col": target_col if target_col else detect_date_and_target(pd.read_csv(file_path))[1],
            "has_regressors": bool(regressor_names),
            "future_periods": future_periods
        }
    }
    
    # Plot actual vs predicted on test
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10,5))
        plt.plot(pred['ds'], pred['y'], label='Actual')
        plt.plot(pred['ds'], pred['yhat'], label='Predicted')
        
        # Determine what we're plotting
        if target_col is None:
            # Check original file to determine what was being plotted
            original_df = pd.read_csv(file_path)
            date_col, target_col = detect_date_and_target(original_df)
        
        # Create more descriptive title and axis labels
        variable_name = target_col if target_col else "Sea Surface Temperature"
        plt.xlabel('Date')
        plt.ylabel(f'{variable_name}')
        plt.title(f'Actual vs Predicted {variable_name} on Test Window')
        
        plt.legend()
        plt.tight_layout()
        
        if save_plots:
            forecast_plot_path = os.path.join(os.path.dirname(save_csv_path), "forecast_plot.png")
            plt.savefig(forecast_plot_path, dpi=300)
            plt.close()
            results["forecast_plot_path"] = os.path.abspath(forecast_plot_path)
            
            # Also save the future forecast plot
            if future_forecast_plot:
                future_forecast_path = os.path.join(os.path.dirname(save_csv_path), "future_forecast_plot.png")
                with open(future_forecast_path, 'wb') as f:
                    f.write(future_forecast_plot.getvalue())
                results["future_forecast_plot_path"] = os.path.abspath(future_forecast_path)
        else:
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            # Add the plot buffer to the results
            results["forecast_plot"] = buf

    except Exception as e:
        print(f"Error creating plot: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
    # Create additional visualization for depth vs parameters
    depth_plots = {}
    if regressor_file_path:
        depth_plots = generate_depth_plots(regressor_file_path, save_dir=os.path.dirname(save_csv_path) if save_plots else None)
    
    # Add depth plots to results
    results["depth_plots"] = depth_plots
    
    # Generate interactive plot JSON
    interactive_plot_json = generate_interactive_forecast_chart(df_p, forecast_full, target_col)
    if interactive_plot_json:
        results["forecast_plot_json"] = interactive_plot_json
    
    # Add new interactive future forecast plot
    interactive_future_forecast_json = generate_interactive_future_forecast_chart(df_p, forecast_full, target_col)
    if interactive_future_forecast_json:
        results["future_forecast_plot_json"] = interactive_future_forecast_json
    
    # Add the future forecast plot to results
    if future_forecast_plot:
        results["future_forecast_plot"] = future_forecast_plot
    
    return results

def generate_interactive_forecast_chart(historical_df, forecast_df, target_col):
    """
    Generates an interactive forecast chart using Plotly.
    
    Args:
        historical_df (pd.DataFrame): DataFrame with historical data ('ds', 'y').
        forecast_df (pd.DataFrame): DataFrame with forecast data from Prophet.
        target_col (str): The name of the target variable being forecast.
        
    Returns:
        str: A JSON string representing the Plotly figure.
    """
    try:
        import plotly.graph_objects as go
        
        fig = go.Figure()

        # Add forecast area
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Upper Forecast'
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0.2)',
            name='Lower Forecast'
        ))

        # Add historical data
        fig.add_trace(go.Scatter(
            x=historical_df['ds'],
            y=historical_df['y'],
            mode='markers',
            name='Historical Data',
            marker=dict(color='black', size=8)
        ))

        # Add forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='blue', width=4)
        ))

        fig.update_layout(
            title=f'Interactive Forecast for {target_col}',
            xaxis_title='Date',
            yaxis_title=target_col,
            showlegend=True
        )
        
        return fig.to_json()
        
    except Exception as e:
        logger.error(f"Error generating interactive forecast chart: {e}")
        return None

def generate_interactive_future_forecast_chart(historical_df, forecast_df, target_col):
    """
    Generates an enhanced interactive forecast chart using Plotly that clearly distinguishes
    between historical data and future predictions.
    
    Args:
        historical_df (pd.DataFrame): DataFrame with historical data ('ds', 'y').
        forecast_df (pd.DataFrame): DataFrame with forecast data from Prophet.
        target_col (str): The name of the target variable being forecast.
        
    Returns:
        str: A JSON string representing the Plotly figure.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Get the date where historical data ends
        historical_end = historical_df['ds'].iloc[-1]
        
        # Separate the forecast into historical period and future period
        historical_forecast = forecast_df[forecast_df['ds'] <= historical_end]
        future_forecast = forecast_df[forecast_df['ds'] > historical_end]
        
        fig = go.Figure()
        
        # Add confidence interval for future forecasts
        fig.add_trace(go.Scatter(
            x=future_forecast['ds'],
            y=future_forecast['yhat_upper'],
            fill=None,
            mode='lines',
            line_color='rgba(255,0,0,0)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=future_forecast['ds'],
            y=future_forecast['yhat_lower'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(255,0,0,0)',
            fillcolor='rgba(255,0,0,0.2)',
            name='95% Confidence Interval',
            hoverinfo='skip'
        ))
        
        # Add historical data points
        fig.add_trace(go.Scatter(
            x=historical_df['ds'],
            y=historical_df['y'],
            mode='markers',
            name='Historical Data',
            marker=dict(color='royalblue', size=8, symbol='circle'),
            hovertemplate='%{x|%Y-%m-%d}<br>' + f'{target_col}: ' + '%{y:.2f}<extra>Historical</extra>'
        ))
        
        # Add model fit line for historical period
        fig.add_trace(go.Scatter(
            x=historical_forecast['ds'],
            y=historical_forecast['yhat'],
            mode='lines',
            line=dict(color='gray', width=2, dash='dash'),
            name='Model Fit',
            hovertemplate='%{x|%Y-%m-%d}<br>' + f'Fitted {target_col}: ' + '%{y:.2f}<extra>Model Fit</extra>'
        ))
        
        # Add future forecast line
        fig.add_trace(go.Scatter(
            x=future_forecast['ds'],
            y=future_forecast['yhat'],
            mode='lines',
            line=dict(color='red', width=4),
            name='Future Forecast',
            hovertemplate='%{x|%Y-%m-%d}<br>' + f'Forecast {target_col}: ' + '%{y:.2f}<extra>Forecast</extra>'
        ))
        
        # Add vertical line at present time
        fig.add_vline(
            x=historical_end, 
            line_width=2, 
            line_dash="dash", 
            line_color="black",
            annotation_text="Present",
            annotation_position="top right"
        )
        
        # Enhance the layout
        fig.update_layout(
            title={
                'text': f'Future Forecast for {target_col}',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=24)
            },
            xaxis_title='Date',
            yaxis_title=target_col,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=60, r=60, t=100, b=60),
            # Add a light blue background color
            plot_bgcolor='rgba(240, 248, 255, 0.5)'
        )
        
        # Add range slider
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            )
        )
        
        # Add annotations for key insights
        # Find the minimum and maximum in the future forecast
        if not future_forecast.empty:
            future_min_idx = future_forecast['yhat'].idxmin()
            future_max_idx = future_forecast['yhat'].idxmax()
            
            # Only add annotations if we have enough future data points
            if len(future_forecast) > 5:
                # Annotate minimum forecast
                fig.add_annotation(
                    x=future_forecast.loc[future_min_idx, 'ds'],
                    y=future_forecast.loc[future_min_idx, 'yhat'],
                    text="Min",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="red"
                )
                
                # Annotate maximum forecast
                fig.add_annotation(
                    x=future_forecast.loc[future_max_idx, 'ds'],
                    y=future_forecast.loc[future_max_idx, 'yhat'],
                    text="Max",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="red"
                )
        
        return fig.to_json()
        
    except Exception as e:
        logger.error(f"Error generating interactive future forecast chart: {e}")
        import traceback
        traceback.print_exc()
        return None
