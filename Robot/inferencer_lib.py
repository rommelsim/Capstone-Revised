from tensorflow.keras.preprocessing import image
import tensorflow as tf
import numpy as np
from robot.api.deco import keyword
import os
from robot.api import logger  # Import Robot Framework logger

# class InferencerLibrary:
#     def __init__(self, model_path="vgg16_model.h5"):
#         # self.CLASS_NAMES = ['faulty', 'working']
#         self.w = 128
#         self.h = 128
#         try:
#             self.model = tf.keras.models.load_model(model_path)
#             print(f"Model Loaded: {model_path}")
#         except Exception as e:
#             print(f"Error loading model: {e}")
#             self.model = None

#     @keyword("Preprocess Image")
#     def preprocess_img(self, img):
#         img = image.load_img(img, target_size=(self.w, self.h))
#         img_array = image.img_to_array(img)
#         img_array = np.expand_dims(img_array, axis=0)
#         return img_array

#     @keyword("Predict Image")
#     def predict(self, img):
#         if self.model is None:
#             return "Error: Model not loaded", 0.0

#         img_array = self.preprocess_img(img)
#         prediction = self.model.predict(img_array)[0][0]

#         prediction_class = "working" if prediction >= 0.5 else "faulty"
#         confidence = prediction if prediction > 0.5 else 1 - prediction

#         print(f"Raw Prediction: {prediction}")
#         print(f"Predicted Class: {prediction_class} with confidence {confidence:.2f}")

#         return prediction_class, confidence

MODEL = "vgg16_model.h5"
DIRECTORY = r"pictures/"
w = 128
h = 128

def preprocess_img(img):
    img = image.load_img(img, target_size=(w, h))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def LoadModel(model_path):
    model = tf.keras.models.load_model(model_path, compile=False)
    print(f"Model Loaded: {model_path}")
    return model

def Predict(model, img):
    try:
        img_arr = preprocess_img(img)
        
        prediction = model.predict(img_arr)[0][0]
        prediction_class = "working" if prediction >= 0.5 else "faulty"
        confidence = prediction if prediction > 0.5 else 1 - prediction
        # print(f"Raw Prediction: {prediction}")
        print(f"{prediction_class}--->{confidence * 100:.2f}%")
        return prediction_class

    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

@keyword("Predict Directory")
def PredictDirectory(model_path, directory):
    try:
        model = LoadModel(model_path)
        for files in os.listdir(os.path.join(directory)):
            img_path = os.path.join(directory, files)
            print(f"Reading Image:{img_path}")
            result = Predict(model, img_path)
            if result == "faulty":
                logger.error(f"Test Failed: {img_path} is faulty.")
                return "FAIL"
        logger.info("All Images passed.")
        return "PASS"
    except Exception as e:
        print(f"Error loading model or directory: {e}")
        return "FAIL"

       
    
# if __name__ == "__main__":
#     PredictDirectory(MODEL, DIRECTORY)