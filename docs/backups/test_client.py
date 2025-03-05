import requests

# URL del endpoint
url = "http://127.0.0.1:5000/diagnostico"

# Ruta completa de la imagen de prueba (JPG o DICOM)
image_path = "processed_dataset/val/canceroso/1-084.jpg"  # Cambiar la ruta si es necesario

# Abrir la imagen en modo binario
with open(image_path, "rb") as image_file:
    files = {"image": image_file}
    response = requests.post(url, files=files)

# Imprimir la respuesta del servidor
print("Respuesta del servidor:")
print(response.json())
