import tensorflow as tf
import numpy as np
import argparse
from tensorflow.keras.preprocessing import image
import pathlib
import os
# Constants
IMG_W, IMG_H = 128, 128  # Same as training
MODEL_PATH = "model.h5"
CLASS_NAMES = ['faulty', 'working']  # Update based on actual class names

def load_model():
    print("Loading model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
    return model

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(IMG_W, IMG_H))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    # img_array /= 255.0  # Normalize
    return img_array

# Use this function to predict a SINGLE image.
def predict(model, img_path):
    print(f"Loaded image: {img_path}")
    img_array = preprocess_image(img_path)
    prediction = model.predict(img_array)[0][0]  # Extract single value
    predicted_class = CLASS_NAMES[int(prediction > 0.5)]  # Threshold for binary classification
    confidence = prediction if prediction > 0.5 else 1 - prediction
    print(f"Prediction: {predicted_class} (Confidence: {confidence:.2f})")

def main():
    model = load_model()
    
    path = r"test/"
    for images in os.listdir(os.path.join(path)):
        predict(model, os.path.join(path, images))

if __name__ == "__main__":
    main()
