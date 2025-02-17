#################################################################################
#
# Add images\ into current directory before running this script
# images\ should have the classes 'working' and 'faulty' inside
# Eg. images\working\photo.jpg
#     images\faulty\photo.jpg
# 
# 
# 
#  
#
#################################################################################

import pathlib
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.applications import VGG16

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

# model = models.Sequential([
#     layers.Conv2D(64, (3, 3), activation='relu', input_shape=(img_w, img_h, 3)), 
#     layers.BatchNormalization(),
#     layers.MaxPooling2D((2, 2)),    

#     layers.Conv2D(128, (3, 3), activation='relu'),
#     layers.BatchNormalization(),
#     layers.MaxPooling2D((2, 2)),

#     layers.Conv2D(256, (3, 3), activation='relu'),
#     layers.BatchNormalization(),
#     layers.MaxPooling2D((2, 2)),

#     layers.Conv2D(512, (3, 3), activation='relu'),
#     layers.BatchNormalization(),
#     layers.MaxPooling2D((2, 2)),

#     # layers.GlobalAveragePooling2D(),
#     layers.Flatten(),
#     layers.Dense(512, activation='relu'),      
#     layers.Dropout(0.5),
#     layers.Dense(1, activation='sigmoid')
# ])
####################################################


# model = models.Sequential([
#     layers.Conv2D(64, (3, 3), activation='relu', input_shape=(img_w, img_h, 3)), 
#     layers.BatchNormalization(),
#     layers.MaxPooling2D((2, 2)),    

#     layers.Conv2D(128, (3, 3), activation='relu'),
#     layers.BatchNormalization(),

#     layers.Conv2D(256, (3, 3), activation='relu'),
#     layers.BatchNormalization(),

#     layers.Flatten(),
#     layers.Dense(256, activation='relu'),    # Reduced size of the dense layer
#     layers.Dropout(0.5),
#     layers.Dense(1, activation='sigmoid')
# ])

####################################################
# Transfer learning
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(img_w, img_h, 3))
base_model.trainable = False
model = models.Sequential([
    base_model,  
    layers.GlobalAveragePooling2D(),  
    layers.Dense(512, activation='relu'), 
    layers.Dropout(0.5),  
    layers.Dense(1, activation='sigmoid') 
])

####################################################
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=lr),  
    loss='binary_crossentropy',
    metrics=['accuracy']
)

from sklearn.utils.class_weight import compute_class_weight
import numpy as np

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


early_stopping = EarlyStopping(
    monitor='val_loss',       
    patience=5,                   
    restore_best_weights=True     
)

# Train the model with class weights
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    class_weight=class_weight_dict,
    callbacks=[early_stopping]
)

model.save('vgg16_model.h5')

restored_model = tf.keras.models.load_model('vgg16_model.h5')
print(restored_model.summary())