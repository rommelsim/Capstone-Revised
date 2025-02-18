from tensorflow.keras.preprocessing import image
import tensorflow as tf
import numpy as np

class InferencerLibrary:
    def __init__(self, model_path="vgg16_model.h5"):
        # self.CLASS_NAMES = ['faulty', 'working']
        self.w = 128
        self.h = 128
        try:
            self.model = tf.keras.models.load_model(model_path)
            print(f"Model Loaded: {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def preprocess_img(self, img):
        img = image.load_img(img, target_size=(self.w, self.h))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def predict(self, img):
        if self.model is None:
            return "Error: Model not loaded", 0.0

        img_array = self.preprocess_img(img)
        prediction = self.model.predict(img_array)[0][0]

        prediction_class = "working" if prediction >= 0.5 else "faulty"
        confidence = prediction if prediction > 0.5 else 1 - prediction

        print(f"Raw Prediction: {prediction}")
        print(f"Predicted Class: {prediction_class} with confidence {confidence:.2f}")

        return prediction_class, confidence
