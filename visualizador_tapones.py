import cv2
import numpy as np

class VisualizadorTapones:
    def __init__(self, tapones_detectados):
        self.tapones_detectados = tapones_detectados

    def mostrar(self):
        """
        Muestra una ventana con la información de los tapones detectados.
        """
        if not self.tapones_detectados:
            print("No se detectaron tapones.")
            return

        for tapon in self.tapones_detectados:
            image = tapon['imagen']  # Imagen procesada
            color = tapon['color']
            area = tapon['area']
            centro = tapon['centro']
            contorno = tapon['contorno']

            # Mostrar el contorno del tapón en la imagen
            cv2.drawContours(image, [contorno], -1, (0, 255, 0), 2)

            # Añadir la información del tapón en la imagen
            text = f"Color: {color} | Area: {area} | Centro: {centro}"
            cv2.putText(image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Mostrar la imagen procesada
            cv2.imshow(f"Tapón Detectado - {color}", image)

            # Esperar a que se presione una tecla antes de cerrar
            cv2.waitKey(0)
            cv2.destroyAllWindows()