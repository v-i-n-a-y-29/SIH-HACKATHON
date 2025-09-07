# backend/forecast.py
import pandas as pd
import numpy as np
import math
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
from prophet import Prophet  # ensure prophet is installed
import os

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
    df2['ds'] = pd.to_datetime(df2['ds'], errors='coerce')
    df2 = df2.dropna(subset=['ds','y'])
    df2 = df2.sort_values('ds').reset_index(drop=True)
    if df2['ds'].duplicated().any():
        df2 = df2.groupby('ds', as_index=False).mean()
    return df2

def run_prophet(file_path, date_col=None, target_col=None, test_frac=0.2, future_periods=30, save_csv_path="prophet_forecast_output.csv"):
    df_p = prepare_df(file_path, date_col, target_col)
    n = len(df_p)
    n_test = max(1, int(n * test_frac))
    train_df = df_p.iloc[:-n_test].copy()
    test_df = df_p.iloc[-n_test:].copy()
    # Fit
    m = Prophet()
    m.fit(train_df)
    # Create future to cover test horizon
    future = m.make_future_dataframe(periods=n_test, freq='D')
    forecast = m.predict(future)
    # Align predictions to test set
    pred = forecast[['ds','yhat']].merge(test_df[['ds','y']], on='ds', how='inner')
    if pred.empty:
        # fallback align by tails
        pred = forecast[['ds','yhat']].tail(n_test).copy()
        pred['y'] = test_df['y'].values[-n_test:]
    mae = mean_absolute_error(pred['y'], pred['yhat'])
    rmse = math.sqrt(mean_squared_error(pred['y'], pred['yhat']))
    # Fit on full data and forecast future_periods
    m_full = Prophet()
    m_full.fit(df_p)
    future_full = m_full.make_future_dataframe(periods=future_periods, freq='D')
    forecast_full = m_full.predict(future_full)
    # Save last future_periods to CSV
    forecast_to_save = forecast_full[['ds','yhat','yhat_lower','yhat_upper']].tail(future_periods).copy()
    forecast_to_save.to_csv(save_csv_path, index=False)
    # Plot actual vs predicted on test
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10,5))
        plt.plot(pred['ds'], pred['y'], label='Actual')
        plt.plot(pred['ds'], pred['yhat'], label='Predicted')
        plt.xlabel('Date'); plt.ylabel('y'); plt.title('Actual vs Predicted on Test Window')
        plt.legend(); plt.tight_layout(); plt.show()
    except Exception:
        pass
    results = {
        "mae": mae,
        "rmse": rmse,
        "forecast_csv": os.path.abspath(save_csv_path),
        "forecast_full_tail": forecast_to_save
    }
    return results
