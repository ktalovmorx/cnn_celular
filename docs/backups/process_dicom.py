import os
from pydicom import dcmread
from PIL import Image

# Directorios de entrada y salida
input_dir = os.path.abspath(os.path.join("DatasetImg", "Imgs"))  # Ruta absoluta
output_dir = os.path.abspath("processed_dataset")

# Crear carpetas de salida
train_cancer = os.path.join(output_dir, "train", "canceroso")
train_no_cancer = os.path.join(output_dir, "train", "no_canceroso")
val_cancer = os.path.join(output_dir, "val", "canceroso")
val_no_cancer = os.path.join(output_dir, "val", "no_canceroso")
os.makedirs(train_cancer, exist_ok=True)
os.makedirs(train_no_cancer, exist_ok=True)
os.makedirs(val_cancer, exist_ok=True)
os.makedirs(val_no_cancer, exist_ok=True)

# Listar todos los archivos DICOM
all_images = [f for f in os.listdir(input_dir) if f.endswith(".dcm")]

# Dividir automáticamente las imágenes en etiquetas simuladas
split_point = len(all_images) // 2  # Mitad para "canceroso", mitad para "no_canceroso"
labeled_images = {img: "canceroso" if idx < split_point else "no_canceroso" for idx, img in enumerate(all_images)}

# Dividir en entrenamiento y validación (80-20)
cancer_images = [img for img, label in labeled_images.items() if label == "canceroso"]
no_cancer_images = [img for img, label in labeled_images.items() if label == "no_canceroso"]

train_cancer_images = cancer_images[:int(0.8 * len(cancer_images))]
val_cancer_images = cancer_images[int(0.8 * len(cancer_images)):]
train_no_cancer_images = no_cancer_images[:int(0.8 * len(no_cancer_images))]
val_no_cancer_images = no_cancer_images[int(0.8 * len(no_cancer_images)):]

# Procesar y convertir las imágenes
def process_and_save(dicom_path, output_path):
    if not os.path.exists(dicom_path):
        print(f"Archivo no encontrado: {dicom_path}")
        return
    try:
        dicom_image = dcmread(dicom_path)
        img = dicom_image.pixel_array
        img = Image.fromarray(img).convert("RGB")  # Convertir a RGB
        img = img.resize((224, 224))  # Redimensionar
        img.save(output_path)
    except Exception as e:
        print(f"Error procesando {dicom_path}: {e}")

# Procesar imágenes para entrenamiento y validación
for img_name in train_cancer_images:
    dicom_path = os.path.join(input_dir, img_name)
    output_path = os.path.join(train_cancer, img_name.replace(".dcm", ".jpg"))
    process_and_save(dicom_path, output_path)

for img_name in val_cancer_images:
    dicom_path = os.path.join(input_dir, img_name)
    output_path = os.path.join(val_cancer, img_name.replace(".dcm", ".jpg"))
    process_and_save(dicom_path, output_path)

for img_name in train_no_cancer_images:
    dicom_path = os.path.join(input_dir, img_name)
    output_path = os.path.join(train_no_cancer, img_name.replace(".dcm", ".jpg"))
    process_and_save(dicom_path, output_path)

for img_name in val_no_cancer_images:
    dicom_path = os.path.join(input_dir, img_name)
    output_path = os.path.join(val_no_cancer, img_name.replace(".dcm", ".jpg"))
    process_and_save(dicom_path, output_path)
