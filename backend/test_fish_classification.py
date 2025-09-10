"""
Test script for the fish classification service
"""
import os
import sys
from services.fish_classification import predict_image
import tensorflow as tf

def main():
    # Check if TensorFlow is available
    print(f"TensorFlow version: {tf.__version__}")
    
    # Check if the model file exists
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'models', 'fish_classification', 'fish_classifier_model.h5')
    print(f"Model path: {model_path}")
    print(f"Model exists: {os.path.exists(model_path)}")
    
    # Try to predict an image if one is provided
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        if os.path.exists(img_path):
            try:
                print(f"Predicting image: {img_path}")
                species, confidence = predict_image(img_path)
                print(f"Prediction result: {species} ({confidence:.2f}%)")
            except Exception as e:
                print(f"Error predicting image: {e}")
        else:
            print(f"Image not found: {img_path}")
    else:
        print("No image provided for testing")
        print("Usage: python test_fish_classification.py <image_path>")

if __name__ == "__main__":
    main()
