from detectorTaponesMulticolor import DetectorTaponesMulticolor


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

# Clase MainExecutable: Orquesta la ejecución del flujo de trabajo
class MainExecutable:
    def __init__(self, detector):
        """
        Constructor de la clase MainExecutable que recibe un objeto `detector`.
        Este objeto es una instancia de la clase DetectorTaponesMulticolor.
        El propósito de esta clase es usar el detector para procesar imágenes y obtener resultados.
        
        :param detector: Objeto de la clase DetectorTaponesMulticolor
        """
        # Guardamos el objeto detector recibido como un atributo de la clase
        self.detector = detector  # El objeto `detector` tiene los métodos que procesarán las imágenes.
#Clase principal ==> main 
    def ejecutar(self):
        """
        Este método orquesta el flujo de trabajo completo: 
        - Procesa las imágenes si no se ha hecho antes.
        - Obtiene las estimaciones (resultados) del procesamiento.
        - Evita la duplicación, asegurándose de que no se procesen las imágenes más de una vez.
        """
        # Verificamos si el atributo 'estimaciones_obtenidas' está presente en el objeto detector
        # Si no existe, significa que las imágenes aún no se han procesado
        if not hasattr(self.detector, 'estimaciones_obtenidas'):
            print("Iniciando procesamiento de imágenes...")
            # Procesamos las imágenes en la carpeta especificada (se realiza solo una vez)
            self.detector.procesar_directorio()

            # Obtener las estimaciones (resultados) luego de procesar las imágenes
            estimaciones = self.detector.get_estimaciones()

            # Guardamos un atributo 'estimaciones_obtenidas' pra marcar que ya se procesaron las imágenes
            self.detector.estimaciones_obtenidas = True

            print("Estimaciones obtenidas.")
        else:
            # Si las estimaciones ya fueron obtenidas previamente, evitamos procesar de nuevo
            print("Las estimaciones ya han sido obtenidas anteriormente. Evitando duplicación.")
        
        # Retornamos las estimaciones (resultados) obtenidas
        return self.detector.get_estimaciones()  # Devolvemos los resultados procesados


# Código principal que ejecuta el flujo de trabajo cuando el script es ejecutado
if __name__ == "__main__":
    # Definir las rutas de las carpetas de entrada y salida
    input_folder = "../files"  # Carpeta donde se encuentran las imágenes de entrada
    output_folder = "../assets"  # Carpeta donde se guardarán las imágenes procesadas

    # Crear una instancia del detector (DetectorTaponesMulticolor) con los parámetros necesarios
    # Esto incluye las carpetas de entrada y salida, los rangos de color y el área mínima de detección
    detector = DetectorTaponesMulticolor(input_folder, output_folder, color_ranges, min_area=500)
    
    # Crear una instancia de la clase MainExecutable, pasando el detector como argumento
    # El objeto `main` orquestará el flujo de trabajo utilizando el detector
    main = MainExecutable(detector)

    
    