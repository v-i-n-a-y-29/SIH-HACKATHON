"""
Copy the fish classification model from SIH-HACKATHON-shubh to our project.
"""
import os
import shutil
from pathlib import Path

def copy_model():
    # Source model path
    source_model = Path(r"c:\Users\VICTUS\Desktop\SIH Hackathon\SIH-HACKATHON-shubh\data\fish_classifier_model.h5")
    
    # Destination model path
    dest_dir = Path(r"c:\Users\VICTUS\Desktop\SIH Hackathon\ocean-ai-prototype\backend\models\fish_classification")
    dest_model = dest_dir / "fish_classifier_model.h5"
    
    # Check if source model exists
    if not source_model.exists():
        print(f"Source model not found at: {source_model}")
        return False
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Copy the model file
    try:
        shutil.copy2(source_model, dest_model)
        print(f"Model successfully copied to: {dest_model}")
        return True
    except Exception as e:
        print(f"Error copying model: {e}")
        return False

if __name__ == "__main__":
    copy_model()
