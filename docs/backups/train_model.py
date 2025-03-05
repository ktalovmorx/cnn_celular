import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# Configuración del dataset
train_dir = "processed_dataset/train"
val_dir = "processed_dataset/val"
batch_size = 32
img_size = (224, 224)

# Generadores de datos
train_datagen = ImageDataGenerator(rescale=1.0/255.0, rotation_range=20, zoom_range=0.15,
                                   width_shift_range=0.2, height_shift_range=0.2, shear_range=0.15,
                                   horizontal_flip=True, fill_mode="nearest")
val_datagen = ImageDataGenerator(rescale=1.0/255.0)

train_gen = train_datagen.flow_from_directory(train_dir, target_size=img_size,
                                              batch_size=batch_size, class_mode="binary")
val_gen = val_datagen.flow_from_directory(val_dir, target_size=img_size,
                                          batch_size=batch_size, class_mode="binary")

# Modelo base preentrenado
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Congelar capas base

# Añadir capas personalizadas
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
x = Dropout(0.5)(x)
predictions = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=predictions)

# Compilar el modelo
model.compile(optimizer=Adam(learning_rate=0.0001), loss="binary_crossentropy", metrics=["accuracy"])

# Entrenar el modelo
model.fit(train_gen, validation_data=val_gen, epochs=10)

# Guardar el modelo
model.save("models/cancer_diagnosis_model.h5")
