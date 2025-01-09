import cv2
import numpy as np
import os
import imutils
import pandas as pd

class DetectorTaponesMulticolor:
    """
    Clase para detectar tapones de múltiples colores en imágenes.
    Procesa imágenes de un directorio, aplica mejoras de iluminación y segmentación
    basada en colores definidos en rangos HSV.
    """
    def __init__(self, input_folder, output_folder, color_ranges, min_area=0, mostrar_mascaras=False):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.color_ranges = color_ranges
        self.min_area = min_area
        self.mostrar_mascaras = mostrar_mascaras
        self.tapones_detectados = []

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
        Detecta tapones de múltiples colores en una imagen específica, aplicando umbrales Otsu y Watershed para la segmentación.
        """
        image = cv2.imread(imagen_path)
        if image is None:
            print(f"Error al cargar la imagen: {imagen_path}")
            return

        # Redimensionar la imagen para un procesamiento más rápido
        image_resized = imutils.resize(image, width=800)
        
        # Convertir la imagen a espacio de color HSV
        hsv = cv2.cvtColor(image_resized, cv2.COLOR_BGR2HSV)

        # Inicializar máscara final
        final_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        for color_name, (lower_bound, upper_bound) in self.color_ranges.items():
            # Crear máscara para el rango de color actual
            mask = cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))

            # Limpiar la máscara con operaciones morfológicas
            mask_cleaned = cv2.erode(mask, None, iterations=1)
            mask_cleaned = cv2.dilate(mask_cleaned, None, iterations=2)

            # Convertir la máscara a escala de grises
            gray_mask = cv2.cvtColor(cv2.bitwise_and(image_resized, image_resized, mask=mask_cleaned), cv2.COLOR_BGR2GRAY)

            # Aplicar umbral de Otsu
            _, otsu_thresh = cv2.threshold(gray_mask, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Encontrar contornos con el umbral de Otsu
            contours, _ = cv2.findContours(otsu_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Procesar contornos,min area es Opcional 
            for contour in contours:
                if self.min_area == 0 or cv2.contourArea(contour) > self.min_area:
                    cv2.drawContours(image_resized, [contour], -1, (0, 255, 0), 2)  # Dibujar contorno

                    M = cv2.moments(contour)  # Calcular momentos
                    if M["m00"] != 0:
                        # Calcular el centro del contorno
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.circle(image_resized, (cx, cy), 5, (0, 0, 255), -1)

                        # Calcular el área del contorno
                        area = cv2.contourArea(contour)

                        # Obtener el rectángulo delimitador (bounding box)
                        x, y, w, h = cv2.boundingRect(contour)

                        # Calcular el aspecto (relación entre ancho y alto)
                        aspecto = w / float(h) if h != 0 else 0

                        cv2.putText(image_resized, f"{color_name} - Area: {area}", (cx - 50, cy - 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # Textos sobre la imagen

                        # Guardar la información del tapón
                        self.tapones_detectados.append({
                            'color': color_name,
                            'area': area,
                            'centro': (cx, cy),
                            'imagen': image_resized,
                            'posicion': (x, y),
                            'ancho': w,
                            'alto': h,
                            'aspecto': aspecto
                        })

            # Realizar segmentación con Watershed
            sure_fg = cv2.erode(mask_cleaned, None, iterations=3)
            sure_bg = cv2.dilate(mask_cleaned, None, iterations=3)
            unknown = cv2.subtract(sure_bg, sure_fg)

            # Crear los marcadores para Watershed
            _, markers = cv2.connectedComponents(sure_fg)
            markers = markers + 1
            markers[unknown == 255] = 0

            # Aplicar Watershed
            markers = cv2.watershed(image_resized, markers)
            image_resized[markers == -1] = [255, 0, 0]  # Bordes en rojo

            # Acumular la máscara final
            final_mask = cv2.bitwise_or(final_mask, mask_cleaned)

        # Guardar imágenes procesadas
        filename = os.path.basename(imagen_path)
        output_image_path = os.path.join(self.output_folder, f"contornos_{filename}")
        output_segmented_path = os.path.join(self.output_folder, f"segmentada_{filename}")

        # Guardar la imagen con los contornos dibujados
        cv2.imwrite(output_image_path, image_resized)
        print(f"Imagen procesada guardada: {output_image_path}")

        # Guardar la máscara segmentada acumulada
        cv2.imwrite(output_segmented_path, final_mask)
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

    def get_estimaciones(self):
        """
        Devuelve un resumen estructurado de las estimaciones calculadas.
        Agrupa por colores, mostrando detalles de cada detección en formato tabular.
        """
        # Lista para almacenar los resultados de todas las detecciones
        resultados = []

        for tapon in self.tapones_detectados:
            color = tapon['color']
            area = tapon['area']
            centro = tapon['centro']
            posicion = tapon['posicion']
            ancho = tapon['ancho']
            alto = tapon['alto']
            aspecto = tapon['aspecto']

            # Añadir los resultados a la lista
            resultados.append({
                'Color': color,
                'Área': area,
                'Centro': centro,
                'Posición': posicion,
                'Ancho': ancho,
                'Alto': alto,
                'Aspecto': aspecto
            })
        
        # Convertir la lista de resultados a un DataFrame de pandas para tener una tabla organizada
        df_resultados = pd.DataFrame(resultados)

        # Calcular estadísticas adicionales
        resumen_estadisticas = df_resultados.groupby('Color').agg(
            total_detectados=('Color', 'count'),
            area_promedio=('Área', 'mean'),
            area_total=('Área', 'sum')
        ).reset_index()

        # Organizar la salida final con estadísticas por color
        for index, row in resumen_estadisticas.iterrows():
            color = row['Color']
            detecciones_color = df_resultados[df_resultados['Color'] == color]
            detalles_color = detecciones_color[['Área', 'Centro', 'Posición', 'Ancho', 'Alto', 'Aspecto']]

            print(f"Resumen para el color {color}:")
            print(detalles_color)
            print(f"Total de tapones detectados: {row['total_detectados']}")
            print(f"Área promedio: {row['area_promedio']:.2f}")
            print(f"Área total: {row['area_total']}")
            print("-" * 50)

        # Retornar el DataFrame con estadísticas resumidas
        return resumen_estadisticas


color_ranges = {
    "Azul": ([100, 50, 50], [140, 255, 255]),
    "Verde": ([35, 50, 50], [85, 255, 255]),
    "Rojo_Rango1": ([0, 50, 50], [10, 255, 255]),
    "Rojo_Rango2": ([170, 50, 50], [180, 255, 255]),
    "Amarillo": ([20, 50, 50], [30, 255, 255]),
    "Negro": ([0, 0, 0], [180, 255, 50]),
    "Rosa": ([140, 50, 50], [170, 255, 255]),
    "Rosa_Claro": ([140, 20, 180], [170, 80, 255]),
    "Blanco_Ajustado": ([90, 10, 180], [130, 60, 255])
}

# Rutas de entrada y salida
input_folder = "../imagenes_tapon"
output_folder = "../imagenes_tapon_detectados"

# Crear instancia de la clase y procesar imágenes
detector = DetectorTaponesMulticolor(input_folder, output_folder, color_ranges, min_area=500)
detector.procesar_directorio()

# Obtener las estimaciones de los tapones detectados
estimaciones = detector.get_estimaciones()