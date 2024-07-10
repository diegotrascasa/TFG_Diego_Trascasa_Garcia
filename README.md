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
