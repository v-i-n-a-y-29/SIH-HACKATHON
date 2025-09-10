"""
Fish Classification Model Module

This module provides functionality for loading and using the fish classification model.
The model is trained to recognize different fish species from images.
"""
import tensorflow as tf
import numpy as np
import os
from PIL import Image
import io

class FishClassifier:
    """Fish Species Classification Model"""
    
    def __init__(self):
        """Initialize the fish classifier model"""
        self.model = None
        self.class_names = None
        self.image_size = (224, 224)
        self.model_path = os.path.join(os.path.dirname(__file__), 'fish_classifier_model.h5')
        
    def load_model(self):
        """Load the trained model and class names"""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            
            # Define the class labels directly since we may not have the training directory
            # These should match the same order used during training
            self.class_names = [
                'Black Sea Sprat', 'Gilt-Head Bream', 'Hourse Mackerel', 'Red Mullet', 
                'Red Sea Bream', 'Sea Bass', 'Shrimp', 'Striped Red Mullet', 'Trout'
            ]
            
            print("✅ Fish classification model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading fish classification model: {e}")
            return False
    
    def predict(self, image_data):
        """
        Predict fish species from image data
        
        Args:
            image_data: Image data as bytes or file path
            
        Returns:
            tuple: (predicted_species, confidence_percentage)
        """
        if self.model is None:
            success = self.load_model()
            if not success:
                return "Error", 0.0
        
        try:
            # Handle different input types
            if isinstance(image_data, str):
                # It's a file path
                image = Image.open(image_data).convert("RGB")
            elif isinstance(image_data, bytes):
                # It's bytes data
                image = Image.open(io.BytesIO(image_data)).convert("RGB")
            else:
                # Assume it's already a PIL image
                image = image_data
                
            # Preprocess the image
            image = image.resize(self.image_size)
            img_array = tf.keras.preprocessing.image.img_to_array(image)
            img_array = np.expand_dims(img_array, axis=0) / 255.0
            
            # Make prediction
            predictions = self.model.predict(img_array)
            
            # Get the predicted class and confidence
            predicted_index = np.argmax(predictions[0])
            predicted_class = self.class_names[predicted_index]
            confidence = float(np.max(predictions[0]) * 100)
            
            return predicted_class, confidence
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return "Error", 0.0

# Create a singleton instance
classifier = FishClassifier()
