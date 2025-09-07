# backend/main.py
from fastapi import FastAPI, UploadFile, File
import os, shutil
from forecast import run_prophet, prepare_df
import pandas as pd

app = FastAPI()
UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def root():
    return {"message":"Ocean AI Forecast API running."}

@app.post("/forecast")
async def forecast(file: UploadFile = File(...), date_col: str = None, target_col: str = None, future_days: int = 30):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # run forecast
    result = run_prophet(file_path, date_col=date_col, target_col=target_col, future_periods=future_days, save_csv_path=os.path.join(UPLOAD_FOLDER, "forecast_output.csv"))
    # return summary (avoid returning large DataFrames)
    return {
        "mae": result["mae"],
        "rmse": result["rmse"],
        "forecast_csv": result["forecast_csv"]
    }

# Optionally: endpoint that returns the prepared ds/y preview
@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    df = prepare_df(file_path)
    return df.head(10).to_dict(orient="records")
