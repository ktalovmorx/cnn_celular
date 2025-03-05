import os
import glob
import shutil
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
from io import BytesIO
import cv2
import requests
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

from dotenv import load_dotenv
load_dotenv()

# -- Leer el archivo .env
try:
    MODEL_NAME = os.getenv('model_name')
    BATCH_SIZE = os.getenv('image_size')
    EPOCHS = os.getenv('batch_size')
    IMAGE_SIZE = os.getenv('epochs')
except Exception as e:
    raise ValueError(f"Error: {e}")


class CNNModel(object):
    IMAGE_SIZE = 224
    BATCH_SIZE = 32
    EPOCHS = 50

    def __init__(self):
        self.directorios = ["train_altogrado", "train_ascus", "train_bajogrado", "train_benigna"]
        self.source_folders = [("./train_altogrado", "./dataset/altogrado"), ("./train_ascus", "./dataset/ascus"), ("./train_bajogrado", "./dataset/bajogrado"), ("./train_benigna","./dataset/benigna")]
        self.procesar_imagenes()
        self.set_folder_minor_image_number()
        self.create_image_generator()

    @staticmethod
    def load_h5_model(self, model_path:str):
        '''
        Cargar el modelo desde el archivo H5
        '''
        return load_model(f"{model_path}")
    
    @staticmethod
    def categorizador_web(model:object, url:str) -> int:
        res = requests.get(url)
        img = Image.open(BytesIO(res.content))
        img = np.array(img).astype(float)/255
        img = cv2.resize(img, (224,224))
        prediccion = model.predict(img.reshape(-1, 224, 224, 3))
        return np.argmax(prediccion[0], axis=-1)

    @staticmethod
    def categorizador_local(model:object, path:str) -> int:
        img = Image.open(path)
        img = np.array(img).astype(float)/255
        img = cv2.resize(img, (CNNModel.IMAGE_SIZE, CNNModel.IMAGE_SIZE))
        prediccion = model.predict(img.reshape(-1, CNNModel.IMAGE_SIZE, CNNModel.IMAGE_SIZE, 3))
        return np.argmax(prediccion[0], axis=-1)

    @staticmethod
    def redimensiona_imagen(image_path:str) -> None:
        '''
        Carga una imagen y cambia sus dimensiones
        '''

        # -- Abre la imagen
        imagen = Image.open(image_path)

        # -- Definir anchura y altura a aplicar
        width = height = CNNModel.IMAGE_SIZE

        # -- Redimensiona la imagen
        imagen = imagen.resize((width, height), Image.LANCZOS)

        # -- Sobreescribe la imagen con las nuevas dimensiones
        imagen.save(image_path)

    def procesar_imagenes(self):
        '''
        Procesa todas las imagenes de los directorios
        '''

        directorios = ["train_altogrado", "train_ascus", "train_bajogrado", "train_benigna"]
        for _dir in self.directorios:
            # -- Establecemos el directorio base
            directorio = f"{os.getcwd()}\\" + _dir

            # -- Obtenemos todos los archivos presentes en el directorio
            archivos_jpg = glob.glob(os.path.join(directorio, '*.jpg'))
            archivos_jpeg = glob.glob(os.path.join(directorio, '*.jpeg'))
            archivos_png = glob.glob(os.path.join(directorio, '*.png'))
            archivos_tiff = glob.glob(os.path.join(directorio, '*.tiff'))

            #-- Concatenamos los resultados
            archivos = archivos_jpg + archivos_jpeg + archivos_png + archivos_tiff

            for f in archivos:
                CNNModel.redimensiona_imagen(f)

    def set_folder_minor_image_number(self):
        '''
        Asigna el total de imagenes de las carpetas con la categoria que tiene menos numero de imagenes
        '''

        # -- Mostramos el total de imagenes por carpeta
        totales = []
        # -- Obtenemos el total de caracteres maximo del nombre de las rutas para hacer un formateo
        longitud_maxima = max(len(d) for d in self.directorios)

        for show_folder in self.directorios:
            totales.append(len(os.listdir(show_folder)))
            # -- Mostramos el texto formateado a la misma longitud de cadena
            print(f'{show_folder.ljust(longitud_maxima)} \t-> {totales[-1]}')
        CNNModel.MENOR = min(totales)
        print(f"Reduciremos el total de imagenes a {CNNModel.MENOR}")

        # -- Copiamos las imagenes a la carpeta de destino
        source_folders = [("./train_altogrado", "./dataset/altogrado"), ("./train_ascus", "./dataset/ascus"), ("./train_bajogrado", "./dataset/bajogrado"), ("./train_benigna","./dataset/benigna")]
        for sf in source_folders:
            carpeta_fuente = sf[0]
            carpeta_destino = sf[1]

            # -- Si no existe la carpeta de destino entonces la creamos
            os.makedirs(carpeta_destino, exist_ok=True)

            sf_images = os.listdir(carpeta_fuente)
            for i, image_name in enumerate(sf_images):

                # -- Limita el total de imagenes a utilizar de acuerdo a la carpeta con menor numero de imagenes
                if i < CNNModel.MENOR:
                    shutil.copy('./' + carpeta_fuente + '/' + image_name, './' + carpeta_destino + '/' + image_name)

    def create_image_generator(self):
        '''
        Crear un generador de imagenes
        '''

        # -- Crea el dataset generador
        datagen = ImageDataGenerator(rescale=1./255, rotation_range=30, width_shift_range=0.25, height_shift_range=0.25, shear_range=15,  zoom_range=[0.5, 1.5], validation_split=0.2)

        # -- Crear el set de datos y pruebas
        self.data_gen_entrenamiento = datagen.flow_from_directory(
                                                            './dataset/',
                                                            target_size = (CNNModel.IMAGE_SIZE, CNNModel.IMAGE_SIZE),
                                                            batch_size=CNNModel.BATCH_SIZE,
                                                            shuffle=True,
                                                            subset='training' # 80% de los datos .. el campo subset solo puede ser training o validation
                                                            )
        self.data_gen_pruebas = datagen.flow_from_directory(
                                                            './dataset/',
                                                            target_size = (CNNModel.IMAGE_SIZE, CNNModel.IMAGE_SIZE),
                                                            batch_size=CNNModel.BATCH_SIZE,
                                                            shuffle=True,
                                                            subset='validation' # 20% de los datos .. el campo subset solo puede ser training o validation
                                                            )

        # -- BATCH = 32, significa que cada iteración de la generación de datos procesará 32 imágenes a la vez.

        print(self.data_gen_entrenamiento.class_indices , f'BATCHES = {len(self.data_gen_entrenamiento)}')
        print(self.data_gen_pruebas.class_indices, f'BATCHES = {len(self.data_gen_pruebas)}')

    def save_predictor(self, predictor_path:str):
        '''
        Almacena el predictor en un archivo
        '''

        data = {v:k for k,v in self.data_gen_entrenamiento.class_indices.items()}
        with open(predictor_path, 'wb') as f:
            pickle.dump(data, f)

    def get_predictor(self, predictor_path:str):
        '''
        Obtiene el predictor desde un archivo
        '''

        with open(predictor_path, 'rb') as f:
            return pickle.load(f)

    def create_model(self):
        '''
        Crea el modelo CNN
        '''

        print('Creando el modelo...')
        # -- Cargar el modelo preentrenado de MobileNetV2 desde TensorFlow Hub
        url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4"
        mobile_net_v2 = hub.KerasLayer(url, input_shape=(224, 224, 3), trainable=False)

        # -- INPUT SHAPE es la forma de entrada que espera el modelo, en este caso 224x224x3

        # -- Definir el modelo secuencial
        modelo = tf.keras.Sequential([
            mobile_net_v2,
            tf.keras.layers.Dense(4, activation="softmax")
        ])

        # -- Construir el modelo con la forma de entrada esperada
        # -- El None en este caso indica que puede recibir cualquier cantidad de imagenes
        print('Construyendo el modelo...')
        modelo.build((None, CNNModel.IMAGE_SIZE, CNNModel.IMAGE_SIZE, 3))

        print('Compilando el modelo...')
        modelo.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        # -- Entrenar el modelo
        print('Entrenando modelo...')
        modelo.fit(
            self.data_gen_entrenamiento,
            epochs=CNNModel.EPOCHS,
            batch_size=CNNModel.BATCH_SIZE,
            validation_data=self.data_gen_pruebas
        )

        print('Salvando modelo...')
        modelo.save("modelo.h5")


if __name__ == '__main__':
    cnn = CNNModel()
    cnn.create_model()
    cnn.save_predictor(predictor_path=MODEL_NAME)