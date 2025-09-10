"""
eDNA Model Manager

This module manages the loading and persistence of the eDNA model
to avoid retraining the model on every server restart.
"""
import os
import pickle
from services.edna_analysis import train_edna_model

# Global variables for model persistence
clf = None
vectorizer = None
edna_model_trained = False

# Paths for model serialization
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'edna')
CLF_PATH = os.path.join(MODEL_DIR, 'clf.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'vectorizer.pkl')

def ensure_model_dir():
    """Ensure the model directory exists"""
    os.makedirs(MODEL_DIR, exist_ok=True)

def save_model():
    """Save the model to disk"""
    global clf, vectorizer
    
    if clf is None or vectorizer is None:
        return False
    
    ensure_model_dir()
    
    try:
        with open(CLF_PATH, 'wb') as f:
            pickle.dump(clf, f)
        
        with open(VECTORIZER_PATH, 'wb') as f:
            pickle.dump(vectorizer, f)
        
        print("eDNA model saved to disk")
        return True
    except Exception as e:
        print(f"Error saving eDNA model: {e}")
        return False

def load_model():
    """Load the model from disk if available"""
    global clf, vectorizer, edna_model_trained
    
    if not os.path.exists(CLF_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("No saved eDNA model found on disk")
        return False
    
    try:
        with open(CLF_PATH, 'rb') as f:
            clf = pickle.load(f)
        
        with open(VECTORIZER_PATH, 'rb') as f:
            vectorizer = pickle.load(f)
        
        edna_model_trained = True
        print("eDNA model loaded from disk")
        return True
    except Exception as e:
        print(f"Error loading eDNA model from disk: {e}")
        return False

def init_model(data_dir):
    """Initialize the model, trying to load from disk first"""
    global clf, vectorizer, edna_model_trained
    
    # First try to load from disk
    if load_model():
        return True
    
    # If loading fails, try to train with sample data
    sample_fasta_path = os.path.join(data_dir, "sample_sequences.fasta")
    if os.path.exists(sample_fasta_path):
        try:
            print(f"Training eDNA model on {sample_fasta_path}")
            clf, vectorizer = train_edna_model(sample_fasta_path)
            edna_model_trained = True
            save_model()  # Save for future use
            print("Trained eDNA model successfully")
            return True
        except Exception as e:
            print(f"Error training eDNA model: {e}")
            return False
    else:
        print(f"Sample FASTA file not found at {sample_fasta_path}. Will train on first upload.")
        return False

def get_model():
    """Get the current model"""
    global clf, vectorizer
    return clf, vectorizer

def train_new_model(file_path):
    """Train a new model with the given file"""
    global clf, vectorizer, edna_model_trained
    
    try:
        print(f"Training model on uploaded file: {file_path}")
        clf, vectorizer = train_edna_model(file_path)
        edna_model_trained = True
        save_model()  # Save for future use
        print("Trained eDNA model successfully")
        return True
    except Exception as e:
        print(f"Error training eDNA model: {e}")
        return False
