import os
import sys

# Agregamos la carpeta "src" al path de Python
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.detectorTaponesMulticolor import DetectorTapones

if __name__ == "__main__":
    # Definimos rutas absolutas para mayor compatibilidad
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(BASE_DIR, "cfg/config.json")
    input_folder = os.path.join(BASE_DIR, "files")

    # Verificamos si el archivo de configuración existe
    if not os.path.exists(config_path):
        print(f"Error: No se encontró el archivo de configuración en '{config_path}'.")
        exit(1)

    # Creamos instancia del detector con la configuración y la ruta base
    detector = DetectorTapones(config_path=config_path, base_dir=BASE_DIR)

    # Verificamos si la carpeta de imágenes existe
    if not os.path.exists(input_folder):
        print(f"Error: No existe la carpeta '{input_folder}'.")
        exit(1)

    # Obtenemos lista de imágenes en la carpeta
    imagenes = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(('.jpg', '.png', '.jpeg'))
    ]

    if not imagenes:
        print("No hay imágenes en la carpeta.")
        exit(1)

    # Procesamos imágenes
    detecciones = detector.procesar(imagenes)

    # Mostramos resultados
    for resultado in detecciones:
        print(f"\nImagen: {os.path.basename(resultado['imagen'])}")
        for tapon in resultado['detecciones']:
            print(f"  Color: {tapon['color']}, Área: {tapon['area']}, Posición: {tapon['posicion']}")