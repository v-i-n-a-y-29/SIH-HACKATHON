"""
Fish Classification Model Training Script

This script trains a fish classification model using the provided dataset.
"""
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Configuration parameters
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.001
MODEL_SAVE_PATH = 'models/fish_classification/fish_classifier_model.h5'

# Data paths
DATA_DIR = 'data/fish dataset'
TRAIN_DIR = os.path.join(DATA_DIR, 'seg_train')
TEST_DIR = os.path.join(DATA_DIR, 'seg_test')

def create_model(num_classes):
    """
    Create a fish classification model based on MobileNetV2.
    
    Args:
        num_classes: Number of fish classes to predict
        
    Returns:
        A compiled Keras model
    """
    # Use MobileNetV2 as base model (smaller and faster than other models)
    base_model = MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze the base model layers
    for layer in base_model.layers:
        layer.trainable = False
    
    # Add classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    # Final model
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile the model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model():
    """
    Train the fish classification model.
    """
    # Create data generators with augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    # Load validation data if available, otherwise use a split from training
    try:
        validation_generator = test_datagen.flow_from_directory(
            TEST_DIR,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='categorical'
        )
        use_validation = True
    except:
        print(f"Test directory {TEST_DIR} not found or empty. Using validation split from training data.")
        use_validation = False
    
    # Get the number of classes
    num_classes = len(train_generator.class_indices)
    print(f"Number of fish classes found: {num_classes}")
    print(f"Class mapping: {train_generator.class_indices}")
    
    # Create the model
    model = create_model(num_classes)
    print(model.summary())
    
    # Set up callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_accuracy',
            patience=5,
            restore_best_weights=True
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=0.00001
        ),
        ModelCheckpoint(
            MODEL_SAVE_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Ensure the model directory exists
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    # Train the model
    if use_validation:
        history = model.fit(
            train_generator,
            epochs=EPOCHS,
            validation_data=validation_generator,
            callbacks=callbacks
        )
    else:
        history = model.fit(
            train_generator,
            epochs=EPOCHS,
            validation_split=0.2,
            callbacks=callbacks
        )
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.tight_layout()
    plt.savefig('models/fish_classification/training_history.png')
    
    # Fine-tune the model (unfreeze some layers)
    print("Fine-tuning the model...")
    # Unfreeze some layers for fine-tuning
    for layer in model.layers:
        layer.trainable = True
    
    # Recompile the model with a lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE/10),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Fine-tune for a few more epochs
    if use_validation:
        history_ft = model.fit(
            train_generator,
            epochs=5,
            validation_data=validation_generator,
            callbacks=callbacks
        )
    else:
        history_ft = model.fit(
            train_generator,
            epochs=5,
            validation_split=0.2,
            callbacks=callbacks
        )
    
    # Save the class indices mapping
    class_indices = train_generator.class_indices
    class_names = {v: k for k, v in class_indices.items()}
    
    # Save class names to a file
    with open('models/fish_classification/class_names.txt', 'w') as f:
        for idx, name in class_names.items():
            f.write(f"{idx},{name}\n")
    
    print(f"Model training complete. Model saved to {MODEL_SAVE_PATH}")
    print(f"Class names saved to models/fish_classification/class_names.txt")
    
    return model

if __name__ == "__main__":
    train_model()
