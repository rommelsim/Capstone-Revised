from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk

import tensorflow as tf
import numpy as np
import argparse
from tensorflow.keras.preprocessing import image
import pathlib
import os

# Note: classes are {'faulty', 'working'}
# Hence, labels are {0, 1}
class InferencerClass:
    def __init__(self, model_path):
        self.CLASS_NAMES = ['faulty', 'working']  # Update based on actual class names
        self.w = 128
        self.h = 128
        self.model = tf.keras.models.load_model(model_path)
        print(f"Model Loaded: {model_path}")
        print(self.model.summary())


    def preprocess_img(self, img):
        img = image.load_img(img, target_size=(self.w,self.h))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis = 0)
        # img_array /= 255.0  # Normalize
        return img_array

    def predict(self, img):
        img_array = self.preprocess_img(img)
        prediction = self.model.predict(img_array)[0][0]
        # prediction_class = self.CLASS_NAMES[int(prediction) >= 0.5]

        # if prediction < 0.5:
        #     prediction_class = "faulty"
        # else:
        #     prediction_class = "working"

        if prediction >= 0.5:
            prediction_class = "working"
        else:
            prediction_class = "faulty"

        print(f"Raw Prediction: {prediction}")
        print(f"Predicted Class: {prediction_class}")

        confidence = prediction if prediction > 0.5 else 1-prediction
        return prediction_class, confidence

class RendererClass:
    def __init__(self, inferencer):
        self.inferencer = inferencer
        self.root = Tk()
        self.root.title("Inferencer")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#0C0C0C")

         # Change icon
        try:
            self.root.iconbitmap("razer.ico")  # Ensure you have an 'icon.ico' file
        except:
            print("Icon not found, skipping...")

        self.title_label = Label(self.root, text="RAZER AI TOOL", fg="#44FF44", bg="#0C0C0C", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)
        
        self.frame = Frame(self.root, bg="#0C0C0C")
        self.frame.pack(fill="both", expand=True, pady=10)

        self.load_img_btn = Button(self.frame, text="Load Image", command=self.open_img, fg="#0C0C0C", bg="#44FF44", 
                                   font=("Arial", 12, "bold"), relief=FLAT, width=15, height=2, activebackground="#66FF66")
        self.load_img_btn.pack(pady=10)

        self.image_label = Label(self.frame, bg="#0C0C0C")
        self.image_label.pack(pady=5)
        
        self.result_label = Label(self.frame, text="", fg="#44FF44", bg="#0C0C0C", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=10)
        
        self.quit_btn = Button(self.frame, text="Quit", command=self.root.destroy, fg="#0C0C0C", bg="#44FF44", 
                               font=("Arial", 12, "bold"), relief=FLAT, width=15, height=2, activebackground="#66FF66")
        self.quit_btn.pack(pady=10)

        self.img_tk = None
        self.root.mainloop()

    def openfn(self):
        filename = filedialog.askopenfilename(title='Open', filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        return filename

    def open_img(self):
        img_path = self.openfn()    
        img = Image.open(img_path)
        img = img.resize((450, 450), Image.Resampling.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.img_tk)

        # Run inference upon loaded image
        pred_class, confidence = self.inferencer.predict(img_path)
        color = "red" if pred_class == "faulty" else "green"
        self.result_label.config(text=f"Result: {pred_class} {confidence * 100:.2f}%" , foreground=color)

class System:
    def __init__(self):
        self.inferencer = InferencerClass('vgg16_model.h5')
        self.render = RendererClass(self.inferencer)
        

driver = System()





