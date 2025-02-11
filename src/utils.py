import cv2
import os

class Utils:
    @staticmethod
    def crear_carpeta(path):
        """Creamos una carpeta si no existe"""
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def cargar_imagen(path):
        """Cargamos una imagen desde un archivo dado"""
        return cv2.imread(path)

    @staticmethod
    def guardar_imagen(imagen, path):
        """Guardamos  una imagen en un archivo"""
        cv2.imwrite(path, imagen)