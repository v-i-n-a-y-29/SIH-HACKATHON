"""
Configuration module for the Ocean AI application
"""
import os
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
MODEL_DIR = ROOT_DIR / "models"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# Model paths
FISH_MODEL_PATH = MODEL_DIR / "fish_classification" / "fish_classifier_model.h5"
EDNA_MODEL_PATH = MODEL_DIR / "edna" / "edna_model.pkl"

# Data paths
SAMPLE_FASTA_PATH = DATA_DIR / "sample_sequences.fasta"
FISH_STOCK_DATA = DATA_DIR / "fish_stock_data.csv"
SST_DATA = DATA_DIR / "SST_Final.csv"
MERGED_DATA = DATA_DIR / "MergedData.csv"

# API settings
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "Ocean AI Analysis API"
VERSION = "1.0.0"
DESCRIPTION = """
Ocean AI Analysis API for:
* Fish Classification
* eDNA Analysis
* Fish Stock Prediction
* Ocean Data Analysis and Forecasting
"""
