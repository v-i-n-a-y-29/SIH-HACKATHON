# backend/run_local_forecast.py
from services.forecast import run_prophet
import os
DATA_PATH = os.path.join("data","ocean_dataset_cleaned.csv")
if __name__ == "__main__":
    out = run_prophet(DATA_PATH, future_periods=30, save_csv_path="data/prophet_30day.csv")
    print("MAE:", out["mae"])
    print("RMSE:", out["rmse"])
    print("Saved forecast to:", out["forecast_csv"])
