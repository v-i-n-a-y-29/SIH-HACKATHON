"""
eDNA analysis endpoints
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import pickle
from pathlib import Path
import logging
from app.services.edna_analysis import analyze_edna, check_invasive, train_edna_model

router = APIRouter()

# Set up logger
logger = logging.getLogger(__name__)

# Define model paths
MODEL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
MODEL_PATH = MODEL_DIR / "edna_model.pkl"
SAMPLE_FASTA = MODEL_DIR / "sample_sequences.fasta"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Load or train the model
def get_edna_model():
    """Get or train the eDNA model"""
    try:
        if MODEL_PATH.exists():
            logger.info(f"Loading eDNA model from {MODEL_PATH}")
            with open(MODEL_PATH, 'rb') as f:
                model_data = pickle.load(f)
                return model_data['clf'], model_data['vectorizer']
        else:
            logger.info(f"Training new eDNA model from {SAMPLE_FASTA}")
            clf, vectorizer = train_edna_model(str(SAMPLE_FASTA))
            os.makedirs(MODEL_PATH.parent, exist_ok=True)
            with open(MODEL_PATH, 'wb') as f:
                pickle.dump({'clf': clf, 'vectorizer': vectorizer}, f)
            return clf, vectorizer
    except Exception as e:
        logger.error(f"Error loading/training eDNA model: {e}")
        return None, None

# Load model once at startup
clf, vectorizer = get_edna_model()

@router.post("/analyze")
async def analyze_edna_sequence(file: UploadFile = File(...)):
    """
    Analyze eDNA sequence data for species detection and invasive species alerts.
    """
    try:
        # Save the uploaded file into the backend/data directory
        upload_path = MODEL_DIR / file.filename
        file_path = str(upload_path)
        with open(file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Analyze the sequence using the loaded model
        global clf, vectorizer
        if clf is None or vectorizer is None:
            # Cold start: train the model on provided FASTA, then persist it
            try:
                logger.info("eDNA model not found; training from uploaded FASTA...")
                clf, vectorizer = train_edna_model(file_path)
                with open(MODEL_PATH, 'wb') as f:
                    pickle.dump({'clf': clf, 'vectorizer': vectorizer}, f)
                logger.info(f"eDNA model trained and saved to {MODEL_PATH}")
            except Exception as train_err:
                logger.error(f"Failed training eDNA model from uploaded file: {train_err}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to train eDNA model. Ensure the FASTA headers follow 'Scientific_name|Status|Common_name' and try again."}
                )

        results = analyze_edna(file_path, clf, vectorizer)
        invasive = check_invasive(results, clf)
        
        # Return the analysis results
        response = {
            "detected_species": results,
            "invasive_species": invasive
        }
        
        return response
    except Exception as e:
        logger.error(f"Error in eDNA analysis: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to analyze eDNA sequence: {str(e)}"}
        )
