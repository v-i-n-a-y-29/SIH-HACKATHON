# backend/main.py
from fastapi import FastAPI, UploadFile, File
import os, shutil
import pandas as pd

# Import forecast logic
from services.forecast import run_prophet, prepare_df

# Import eDNA logic
from services.edna_analysis import train_edna_model, analyze_edna

app = FastAPI()
UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- Root ----------------
@app.get("/")
def root():
    return {"message": "Ocean AI Backend running with Forecast + eDNA"}

# ---------------- Forecast Endpoint ----------------
@app.post("/forecast")
async def forecast(file: UploadFile = File(...), date_col: str = None, target_col: str = None, future_days: int = 30):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Run Prophet forecast
    result = run_prophet(
        file_path,
        date_col=date_col,
        target_col=target_col,
        future_periods=future_days,
        save_csv_path=os.path.join(UPLOAD_FOLDER, "forecast_output.csv")
    )
    return {
        "mae": result["mae"],
        "rmse": result["rmse"],
        "forecast_csv": result["forecast_csv"]
    }

# ---------------- Data Preview Endpoint ----------------
@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    df = prepare_df(file_path)
    return df.head(10).to_dict(orient="records")

# ---------------- eDNA Analysis Endpoint ----------------
# Train once on the mock sample FASTA
clf, vectorizer = train_edna_model(os.path.join(UPLOAD_FOLDER, "sample_sequences.fasta"))

@app.post("/analyze-edna")
async def analyze_edna_endpoint(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    results = analyze_edna(file_path, clf, vectorizer)
    return {"predicted_species": results}
