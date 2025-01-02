import cv2
import numpy as np
import os
import imutils
from visualizador_tapones import VisualizadorTapones  # Importamos la clase de visualización

class DetectorTaponesMulticolor:
    """
    Clase para detectar tapones de múltiples colores en imágenes.
    Procesa imágenes de un directorio, aplica mejoras de iluminación y segmentación
    basada en colores definidos en rangos HSV.
    """
    def __init__(self, input_folder, output_folder, color_ranges, color_names, min_area=500, mostrar_mascaras=False):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.color_ranges = color_ranges
        self.color_names = color_names
        self.min_area = min_area
        self.mostrar_mascaras = mostrar_mascaras
        self.tapones_detectados = []  # Lista para almacenar los tapones detectados

        # Crear la carpeta de salida si no existe
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    @staticmethod
    def aplicar_clahe(image):
        """
        Aplica el algoritmo CLAHE (Contrast Limited Adaptive Histogram Equalization)
        para mejorar la uniformidad de la iluminación en la imagen.

        :param image: Imagen en formato BGR.
        :return: Imagen mejorada con CLAHE.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)  # Convertir a espacio de color LAB
        l, a, b = cv2.split(lab)  # Separar canales
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))  # Configuración de CLAHE
        l_clahe = clahe.apply(l)  # Aplicar CLAHE al canal de luminancia

        lab_clahe = cv2.merge((l_clahe, a, b))  # Recomponer la imagen LAB
        return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)  # Convertir de nuevo a BGR

    def detectar_tapon(self, imagen_path):
        """
        Detecta tapones de múltiples colores en una imagen específica.

        :param imagen_path: Ruta de la imagen a procesar.
        """
        image = cv2.imread(imagen_path)
        if image is None:
            print(f"Error al cargar la imagen: {imagen_path}")
            return

        # Redimensionar la imagen para un procesamiento más rápido
        image_resized = imutils.resize(image, width=800)
        # Mejorar la imagen con CLAHE
        image_clahe = self.aplicar_clahe(image_resized)
        # Convertir la imagen a espacio de color HSV
        hsv = cv2.cvtColor(image_clahe, cv2.COLOR_BGR2HSV)

        # Aplicar un filtro de suavizado para reducir el ruido
        hsv = cv2.GaussianBlur(hsv, (5, 5), 0)

        # Inicializar máscara acumulativa
        final_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        # Iterar sobre los rangos de colores
        for i, (lower_bound, upper_bound) in enumerate(self.color_ranges):
            # Crear máscara para el rango de color actual
            mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))
            
            # Limpiar la máscara con operaciones morfológicas
            mask_cleaned = cv2.erode(mask, None, iterations=1)
            mask_cleaned = cv2.dilate(mask_cleaned, None, iterations=2)

            # Mostrar la máscara si está habilitado
            if self.mostrar_mascaras:
                cv2.imshow(f"Mascara Color {i}", mask_cleaned)

            # Acumular la máscara
            final_mask = cv2.bitwise_or(final_mask, mask_cleaned)

        if self.mostrar_mascaras:
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Aplicar la máscara acumulativa a la imagen original
        colormaskHSV_filtered = cv2.bitwise_and(image_resized, image_resized, mask=final_mask)

        # Encontrar contornos en la máscara final
        contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Procesar cada contorno
        for contour in contours:
            if cv2.contourArea(contour) > self.min_area:  # Filtrar por área mínima
                cv2.drawContours(image_resized, [contour], -1, (0, 255, 0), 2)  # Dibujar contorno

                M = cv2.moments(contour)  # Calcular momentos
                if M["m00"] != 0:
                    # Calcular el centro del contorno
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(image_resized, (cx, cy), 5, (0, 0, 255), -1)

                    # Identificar el color del tapón por el color predominante en el contorno
                    color_count = {}

                    # Crear una máscara global para la región del contorno
                    mask_contour = np.zeros_like(final_mask)
                    cv2.drawContours(mask_contour, [contour], -1, (255), thickness=cv2.FILLED)

                    # Iterar sobre los rangos de colores
                    for i, (lower_bound, upper_bound) in enumerate(self.color_ranges):
                        mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))
                        
                        # Aplicar la máscara del contorno sobre la máscara de color
                        mask_color_in_contour = cv2.bitwise_and(mask, mask_contour)
                        
                        # Contar cuántos píxeles del color están dentro del contorno
                        color_count[self.color_names[i]] = cv2.countNonZero(mask_color_in_contour)

                    # Encontrar el color con más píxeles dentro del contorno
                    color_name = max(color_count, key=color_count.get)

                    # Calcular el área del contorno
                    area = cv2.contourArea(contour)
                    cv2.putText(image_resized, f"{color_name} - Area: {area}", (cx - 50, cy - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Guardar la información del tapón
                    self.tapones_detectados.append({
                        'color': color_name,
                        'area': area,
                        'centro': (cx, cy),
                        'imagen': image_resized,  # Guardar la imagen procesada
                        'contorno': contour  # Guardar el contorno también
                    })

        # Guardar imágenes procesadas
        filename = os.path.basename(imagen_path)
        output_image_path = os.path.join(self.output_folder, f"contornos_{filename}")
        output_segmented_path = os.path.join(self.output_folder, f"segmentada_{filename}")

        cv2.imwrite(output_image_path, image_resized)
        cv2.imwrite(output_segmented_path, colormaskHSV_filtered)

        print(f"Imagen procesada guardada: {output_image_path}")
        print(f"Imagen segmentada guardada: {output_segmented_path}")

    def procesar_directorio(self):
        """
        Procesa todas las imágenes en el directorio de entrada.
        Aplica detección de tapones y guarda los resultados.
        """
        # Listar imágenes en el directorio de entrada
        imagenes = [f for f in os.listdir(self.input_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

        for imagen in imagenes:
            imagen_path = os.path.join(self.input_folder, imagen)
            self.detectar_tapon(imagen_path)


# Definir rangos de colores (HSV) ajustados
color_ranges = [
    ([100, 50, 50], [140, 255, 255]),  # Azul
    ([35, 50, 50], [85, 255, 255]),   # Verde
    ([0, 50, 50], [10, 255, 255]),    # Rojo (Rango 1)
    ([170, 50, 50], [180, 255, 255]), # Rojo (Rango 2)
    ([20, 50, 50], [30, 255, 255]),   # Amarillo
    ([0, 0, 0], [180, 255, 50]),      # Negro
    ([140, 50, 50], [170, 255, 255]), # Rosa
    ([140, 20, 180], [170, 80, 255]), # Rosa claro
    ([90, 20, 180], [130, 80, 255]),  # Azul claro
    ([0, 0, 220], [180, 40, 255])     # Blanco ajustado
]

# Nombres de los colores correspondientes a los rangos HSV
color_names = ["Azul", "Verde", "Rojo", "Rojo", "Amarillo", "Negro", "Rosa", "Rosa Claro", "Azul Claro", "Blanco"]

# Rutas de entrada y salida
input_folder = "imagenes_tapon"
output_folder = "imagenes_tapon_detectados"

# Crear instancia de la clase y procesar imágenes
detector = DetectorTaponesMulticolor(input_folder, output_folder, color_ranges, color_names, min_area=500, mostrar_mascaras=False)
detector.procesar_directorio()

# Crear instancia de la clase VisualizadorTapones para mostrar los resultados
visualizador = VisualizadorTapones(detector.tapones_detectados)
visualizador.mostrar()