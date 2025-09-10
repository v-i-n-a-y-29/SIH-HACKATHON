# backend/services/fish_classification.py
"""
Fish Classification Service

This service provides endpoints for the fish classification functionality.
It uses the fish classification model from the models package.
"""
import os
import sys
import tensorflow as tf
from PIL import Image
import numpy as np

# Path to the model file
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                         'models', 'fish_classification', 'fish_classifier_model.h5')

# Path to class names file
CLASS_NAMES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               'models', 'fish_classification', 'class_names.txt')

# Load class names if available, otherwise use default list
def load_class_names():
    if os.path.exists(CLASS_NAMES_PATH):
        class_names = {}
        with open(CLASS_NAMES_PATH, 'r') as f:
            for line in f:
                idx, name = line.strip().split(',', 1)
                class_names[int(idx)] = name
        return class_names
    else:
        # Default class names from the original model
        return {
            0: 'Black Sea Sprat', 
            1: 'Gilt-Head Bream', 
            2: 'Hourse Mackerel', 
            3: 'Red Mullet', 
            4: 'Red Sea Bream', 
            5: 'Sea Bass', 
            6: 'Shrimp', 
            7: 'Striped Red Mullet', 
            8: 'Trout'
        }

# Load the model on startup if possible
model = None
class_names = None
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    class_names = load_class_names()
    print("✅ Fish classification model loaded successfully!")
    print(f"Found {len(class_names)} fish classes")
except Exception as e:
    print(f"❌ Error loading fish classification model: {e}")
    model = None
    class_names = None

def predict_image(img_path):
    """
    Predicts the class of a single image.
    
    Args:
        img_path: Path to the image file
        
    Returns:
        tuple: (predicted_species, confidence_percentage)
    """
    global model, class_names
    
    # Check if the file exists
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image file not found: {img_path}")
    
    # If model not loaded, try to load it
    if model is None:
        try:
            model = tf.keras.models.load_model(MODEL_PATH)
            class_names = load_class_names()
            print("Model loaded successfully on demand.")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    try:
        # Load and preprocess the image
        img = Image.open(img_path).convert("RGB")
        img = img.resize((224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        # Make prediction
        predictions = model.predict(img_array)
        
        # Get the predicted class and confidence
        predicted_index = np.argmax(predictions[0])
        predicted_class = class_names.get(predicted_index, f"Unknown Class {predicted_index}")
        confidence = float(np.max(predictions[0]) * 100)
        
        return predicted_class, confidence
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        raise RuntimeError(f"Error occurred during prediction: {e}")
