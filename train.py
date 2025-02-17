import pathlib
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

img_w = 128
img_h = 128
batch_size = 32
lr = 0.001
epochs = 100

dataset_path = r"images/"
data_dir = pathlib.Path(dataset_path)

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.3,
    subset="training",
    seed=123,
    image_size=(img_w, img_h),
    batch_size=batch_size,
    label_mode="binary"
)
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.3,
    subset="validation",
    seed=123,
    image_size=(img_w, img_h),
    batch_size=batch_size,
    label_mode="binary"
)

class_names = train_ds.class_names
print(f"Classes found: {class_names}")

# CNN Processes:
# 1) Conv2D(): Convolutional Layer. Outputs a feature map. 
# 2) MaxPooling2D((2, 2)): Pooling Layer. Downsamples feature map. 
# 3) Dense(512, activation='relu'): Fully Connected Layer. Feature map flattened to 1D vector, used for predictions.

model = models.Sequential([
    layers.Conv2D(64, (3, 3), activation='relu', input_shape=(img_w, img_h, 3)), 
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),    

    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(256, (3, 3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(512, (3, 3), activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2, 2)),

    # layers.GlobalAveragePooling2D(),
    layers.Flatten(),
    layers.Dense(512, activation='relu'),      
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=lr),  
    loss='binary_crossentropy',
    metrics=['accuracy']
)

from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# # Extract labels from the dataset
# labels = []
# for _, label in train_ds:
#     labels.extend(label.numpy())  # Convert label tensor to numpy array

# # Convert labels to a numpy array
# labels = np.array(labels).flatten()

labels = np.concatenate([y.numpy().flatten() for _, y in train_ds], axis=0)

# Compute class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(labels),
    y=labels
)

# Create a dictionary mapping class labels to class weights
# Less frequent will get a higher weight
# More frequent will get a lower weight
# Concept: Lesser photos == Higher weight
class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}
print(class_weight_dict)

# Train the model with class weights
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    class_weight=class_weight_dict  # Pass the class weights here
)

model.save('model.h5')
