import tensorflow as tf
import numpy as np
import argparse
from tensorflow.keras.preprocessing import image
import pathlib
import os

# Constants
IMG_W, IMG_H = 128, 128  
# MODEL_PATH = "model.h5"
# CLASS_NAMES = ['faulty', 'working'] 

def load_model(model):
    print("Loading model...")
    try:
        model = tf.keras.models.load_model(model)
        model.summary()
        print("Model loaded.")
        return model
    except Exception as e:
        print("Error loading model:", e)


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
    if prediction >= 0.5:
        prediction_class = "working"
    else:
        prediction_class = "faulty"
        
    confidence = prediction if prediction > 0.5 else 1-prediction
    return prediction_class, confidence

# def main():
#     model = load_model()
#     
#     path = r"test/"
#     for images in os.listdir(os.path.join(path)):
#         predict(model, os.path.join(path, images))
# 
# if __name__ == "__main__":
#     main()

