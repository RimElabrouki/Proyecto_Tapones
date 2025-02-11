import cv2
import json
import os
import numpy as np
import imutils
from src.utils import Utils  

class DetectorTapones:
    def __init__(self, config_path, base_dir):
        # Inicializamos la clase Utils
        self.utils = Utils()
        
        # Guardamos la ruta base para su uso posterior
        self.base_dir = os.path.abspath(base_dir)  
        
        # Creamos carpetas necesarias si no existen
        self.utils.crear_carpeta(os.path.join(self.base_dir, "assets"))  
        self.utils.crear_carpeta(os.path.join(self.base_dir, "files"))   
        
        # Cargamos configuración desde el archivo JSON
        with open(config_path, "r") as f:
            config = json.load(f)

        self.color_ranges = config["color_ranges"]
        self.min_area = config.get("min_area", 0)

    def detectar_tapon(self, imagen_path):
        # Cargamos la imagen
        image = self.utils.cargar_imagen(imagen_path)
        if image is None:
            print(f"Error al cargar la imagen: {imagen_path}")
            return []

        # Redimensionamos la imagen y convertirla a espacio de color HSV
        image_resized = imutils.resize(image, width=800)
        hsv = cv2.cvtColor(image_resized, cv2.COLOR_BGR2HSV)
        detecciones = []

        # Detectamos contornos para cada color
        for color_name, (lower_bound, upper_bound) in self.color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))
            mask_cleaned = cv2.erode(mask, None, iterations=1)
            mask_cleaned = cv2.dilate(mask_cleaned, None, iterations=2)

            gray_mask = cv2.cvtColor(cv2.bitwise_and(image_resized, image_resized, mask=mask_cleaned), cv2.COLOR_BGR2GRAY)
            _, otsu_thresh = cv2.threshold(gray_mask, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            contours, _ = cv2.findContours(otsu_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if self.min_area == 0 or cv2.contourArea(contour) > self.min_area:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                        area = cv2.contourArea(contour)
                        x, y, w, h = cv2.boundingRect(contour)
                        aspecto = w / float(h) if h != 0 else 0

                        detecciones.append({
                            'color': color_name,
                            'area': area,
                            'centro': (cx, cy),
                            'posicion': (x, y),
                            'ancho': w,
                            'alto': h,
                            'aspecto': aspecto
                        })

                        # Dibujamos contornos y texto en la imagen
                        cv2.drawContours(image_resized, [contour], -1, (0, 255, 0), 2)
                        cv2.circle(image_resized, (cx, cy), 5, (255, 0, 0), -1)
                        cv2.putText(image_resized, f"{color_name} - Area: {area}", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        # Guardamos imagen procesada
        imagen_name = os.path.basename(imagen_path)
        output_path = os.path.join(self.base_dir, f"assets/procesada_{imagen_name}")
        self.utils.guardar_imagen(image_resized, output_path)
        return detecciones

    def procesar(self, imagen_paths):
        todas_las_detecciones = []
        for imagen_path in imagen_paths:
            detecciones = self.detectar_tapon(imagen_path)
            if detecciones:
                todas_las_detecciones.append({
                    'imagen': imagen_path,
                    'detecciones': detecciones
                })

        return todas_las_detecciones