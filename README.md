# ** Detector de Tapones Multicolor 🎯 **

¡Bienvenido al **Detector de Tapones Multicolor**!  Este proyecto usa procesamiento de imágenes con **OpenCV** para detectar y clasificar tapones en imágenes 📸, ¡y lo hace de manera rápida y precisa! 🎯

## ** Características** 
- **Detección Multicolor**: Detecta tapones de diferentes colores usando rangos definidos en HSV. 🌈
- **Mejora de Iluminación**: ¡Tus imágenes siempre perfectas! Usa CLAHE para mejorar el contraste. 💡
- **Filtrado por Área**: Filtra los tapones que son demasiado pequeños para evitar falsos positivos. 🔍
- **Segmentación de Imágenes**: Crea imágenes segmentadas que resaltan los tapones. 📷
- **Visualización**: Muestra los resultados con contornos y colores de tapones. 👁️ 
- **Configuración Personalizada**: Puedes ajustar parámetros como los rangos de colores y directorios de entrada y salida. ⚙️🔧

## **🛠️ Requisitos** 📦

Este proyecto necesita algunas bibliotecas para funcionar correctamente:

- **OpenCV** (`opencv-python`) 📸
- **NumPy** (`numpy`) ➗
- **imutils** (`imutils`) 💻

Instala las dependencias con el siguiente comando:

```bash
pip install opencv-python numpy imutils

📥 Instalación 📂


1. **Clona el repositorio**:

    ```bash
    git clone https://github.com/tu-usuario/DetectorTaponesMulticolor.git
    ```

2. **Accede a la carpeta del proyecto**:

    ```bash
    cd DetectorTaponesMulticolor
    ```

3. **Crea un entorno virtual** (opcional pero recomendado):

    ```bash
    python -m venv venv
    source venv/bin/activate   # En Linux/Mac
    venv\Scripts\activate      # En Windows
    ```

4. **Instala las dependencias**:

    ```bash
    pip install -r requirements.txt
    ```

---
## **Uso del Proyecto** 

1. **Agrega las imágenes que deseas procesar** a la carpeta `imagenes_tapon/`. 📂
   
2. **Ejecuta el script de detección**:

    ```bash
    python DetectorTaponesMulticolor.py
    ```

3. ¡Listo! Las imágenes procesadas se guardarán en la carpeta `imagenes_tapon_detectados/` con los tapones marcados. 🖼️

---
## 🌈 **Colores Detectados** 🎨

Aquí tienes los colores que este detector puede identificar:

- 🔵 **Azul**
- 🟢 **Verde**
- 🔴 **Rojo** (Rango 1 y 2)
- 🟡 **Amarillo**
- ⚫ **Negro**
- 🌸 **Rosa**
- 🌷 **Rosa Claro**
- 🔵 **Azul Claro**
- ⚪ **Blanco**

---
## 🧑‍💻 **Contribuye al Proyecto** 💡

¿Tienes una idea genial o una mejora para este proyecto? ¡Nos encantaría escucharla! 🎤💬

Si encuentras algún error o deseas agregar una nueva funcionalidad, por favor, **abre un issue** o **haz un pull request**. Todos los aportes son bienvenidos. 🙌

---

## 📄 **Licencia** 📜

Este proyecto está bajo la licencia **MIT**. Puedes ver los detalles de la licencia [aquí](LICENSE).

---

## 📧 **Contacto** 👨‍💻

Desarrollado por **[Tu Nombre]**. Si tienes alguna pregunta o sugerencia, no dudes en contactarme:

- Correo electrónico: [tu-email@dominio.com]
- Twitter: [@tuTwitter]

¡Gracias por usar el proyecto! 😊

---

## 📸 **Ejemplos de Imágenes** 🖼️

Aquí tienes algunos ejemplos de cómo se verán las imágenes procesadas:

![Ejemplo de imagen 1](imagenes_tapon_detectados/contornos_imagen1.jpg)
![Ejemplo de imagen 2](imagenes_tapon_detectados/contornos_imagen2.jpg)

---

**¡Haz que tus proyectos de procesamiento de imágenes sean aún más impresionantes!** 🔥🚀
