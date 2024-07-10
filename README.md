# Aplicación Web de Monitoreo Cardíaco en Tiempo Real con Análisis Predictivo de Tipos de Latidos en ECG.
### Ingeniería de la Salud
#### Autor: Diego Trascasa García
#### Tutor: Guirguis Zaki Guirguis Abdelmessih

# Resumen:

El monitoreo de la actividad cardíaca es crucial para la detección temprana y el manejo adecuado de diversas afecciones cardíacas. Sin embargo, los dispositivos de monitoreo disponibles en el mercado suelen ser caros y complejos a la hora de usarlos, lo que limita su accesibilidad para muchos pacientes.

En respuesta a esta necesidad, se ha desarrollado una aplicación web accesible y económica para el monitoreo cardíaco en tiempo real. Esta herramienta permite a los usuarios conectar el dispositivo de monitoreo cardíaco a través de un puerto serial, visualizar los datos de ECG en tiempo real y guardar las grabaciones para su posterior análisis, dentro de la misma aplicación web.

Continuando con la iniciativa de proporcionar herramientas de apoyo en el ámbito clínico y de ayuda para los pacientes, la aplicación tiene varias funcionalidades clave:

- Conexión y desconexión del dispositivo de monitoreo cardíaco.
- Visualización en tiempo real de los datos de ECG.
- Cálculo y visualización de la frecuencia cardíaca en LPM.
- Grabación y almacenamiento de los datos de ECG.
- Predicción y clasificación de latidos cardíacos usando el modelo de predicción Random Forest.

Se han añadido mejoras adicionales, como la capacidad de guardar los resultados de las predicciones en una base de datos. Esto se realiza mediante un botón que, una vez generadas las predicciones, permite al usuario guardar estos resultados junto con la fecha y hora en la base de datos, la cual, se puede descargar en un fichero CSV. Una página adicional en la aplicación permite la visualización y gestión de esta base de datos, facilitando el acceso a los resultados históricos tanto para pacientes como para profesionales de la salud.


## Estructura de Directorios

### Arduino
Contiene todo el material relacionado con el desarrollo del software para la placa Arduino.
- **version 1**: Scripts iniciales de prueba para los sensores KY039 y AD8232.
  - `KY039_bluetooth.ino`: Prueba del sensor KY039 con el módulo Bluetooth HC-05.
  - `KY039_usb.ino`: Prueba del sensor KY039 con conexión USB.
  - `AD82CONPYTHONYELECTRODOS_bluetooth.ino`: Prueba del sensor AD8232 con Bluetooth HC-05.
  - `AD82CONPYTHONYELECTRODOS_usb.ino`: Prueba del sensor AD8232 con conexión USB.
- **version 2**: Versión final del código de Arduino.
  - `AD8232_usb_y_led.ino`: Código mejorado para el sensor AD8232 con comunicación USB, reducción de ruido, LED sincronizado y auto-calibración.

### fotos
Imágenes utilizadas en la página web de Streamlit.

### data_ecg
Enlace a Google Drive con archivos de entrenamiento, prueba y datos normales de ECG.

### streamlit.py
Código principal de la aplicación web desarrollada con Streamlit para la visualización y análisis de datos de ECG en tiempo real.

### serialmonitor.py
Aplicación de escritorio para la monitorización en vivo y grabación de datos de ECG, desarrollada con Tkinter.

### AnalisisBueno.ipynb
Notebook explicando el proceso de tratamiento de datos y la elección del modelo de predicción Random Forest.

### TFG
Link con una carpeta con todo lo necesario para descargar y que el proyecto funcione correctamente.

### model.py
Script para el entrenamiento del modelo de predicción que genera el archivo `ecg_model.pkl`.

### Diagrama_Gantt.xlsx
Diagrama de Gantt en formato Excel mostrando la planificación temporal del proyecto.

### Documentación_Proyecto
Contiene la memoria del proyecto en formato LaTeX.
- **img**: Imágenes usadas en la memoria y anexos.
- **tex**: Capítulos de la memoria y anexos en formato LaTeX.

### memoria_Diego_Trascasa_García.pdf
Documento PDF con la memoria completa del proyecto.

### anexo_Diego_Trascasa_García.pdf
Documento PDF con el anexo completo del proyecto.

### Video_demostracion
Enlace al video de demostración del funcionamiento del proyecto.
