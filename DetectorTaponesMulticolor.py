import cv2
import numpy as np
import os
import imutils


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

        for i, (lower_bound, upper_bound) in enumerate(self.color_ranges):
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

            # Procesar contornos
            for contour in contours:
                if cv2.contourArea(contour) > self.min_area:  # Filtrar por área mínima
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

                        cv2.putText(image_resized, f"{self.color_names[i]} - Area: {area}", (cx - 50, cy - 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # Textos sobre la imagen

                        # Guardar la información del tapón
                        self.tapones_detectados.append({
                            'color': self.color_names[i],
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


#Metodo para procesar el directorio,procesar la imagenes en el directorio 
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
    #([90, 20, 180], [130, 80, 255]),  # Azul claro
    ([90, 10, 180], [130, 60, 255])  # Rango ajustado entre azul claro y blanco ajustado
    #([0, 0, 220], [180, 40, 255])     # Blanco 
]

def mostrar_resultados(self):
    """ Mostrar los resultados detectados de los tapones sobre las imágenes """
    if not self.tapones_detectados:
        print("No se detectaron tapones.")
        return

    # Recorrer cada tapón detectado y mostrar los resultados sobre las imágenes
    for i, tapon in enumerate(self.tapones_detectados, 1):
        imagen_resultado = tapon['imagen'].copy()  # Hacer una copia de la imagen para modificarla sin perder la original

        color = tapon.get('color', 'No disponible')
        area = tapon.get('area', 'No disponible')
        centro = tapon.get('centro', 'No disponible')
        posicion = tapon.get('Posición', 'No disponible')
        ancho = tapon.get('ancho', 'No disponible')
        alto = tapon.get('alto', 'No disponible')
        aspecto = tapon.get('aspecto', 'No disponible')

        # Dibujar el texto sobre la imagen para mostrar los resultados
        cv2.putText(imagen_resultado, f"Tapón {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Color: {color}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Área: {area}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Centro: {str(centro)}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Pos: {str(posicion)}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Ancho: {ancho}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Alto: {alto}", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(imagen_resultado, f"Aspecto: {aspecto:.2f}", (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Dibujar el contorno y el centro del tapón
        cv2.circle(imagen_resultado, tapon['centro'], 5, (0, 0, 255), -1)  # Centro en rojo
        cv2.rectangle(imagen_resultado, (tapon['Posición'][0], tapon['Posición'][1]), 
                      (tapon['Posición'][0] + tapon['ancho'], tapon['Posición'][1] + tapon['alto']), 
                      (0, 255, 0), 2)  # Rectángulo verde alrededor del tapón

        # Mostrar la imagen con los resultados
        cv2.imshow(f"Tapón {i} - {color}", imagen_resultado)
        
        # Si necesitas guardar las imágenes procesadas con los resultados:
        output_image_path = os.path.join(self.output_folder, f"resultado_tapon_{i}.png")
        cv2.imwrite(output_image_path, imagen_resultado)
        print(f"Imagen resultado guardada: {output_image_path}")

    cv2.waitKey(0)  # Esperar que el usuario cierre la ventana
    cv2.destroyAllWindows()  # Cerrar todas las ventanas abiertas de OpenCV


# Nombres de los colores correspondientes a los rangos HSV
color_names = ["Azul", "Verde", "Rojo", "Rojo", "Amarillo", "Negro", "Rosa", "Rosa Claro","Blanco"]
# Rutas de entrada y salida
input_folder = "imagenes_tapon"
output_folder = "imagenes_tapon_detectados"

# Crear instancia de la clase y procesar imágenes
detector = DetectorTaponesMulticolor(input_folder, output_folder, color_ranges, color_names, min_area=500, mostrar_mascaras=False)
detector.procesar_directorio()