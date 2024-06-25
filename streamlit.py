import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import joblib
from datetime import datetime
from PIL import Image
import threading
import subprocess
import sqlite3

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Sistema de Monitoreo Cardíaco",
    page_icon="fotos/logo.webp",
    layout="wide"
)

# Conectar o crear la base de datos SQLite
conn = sqlite3.connect('predicciones_ecg.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS predicciones (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 fecha_hora TEXT,
                 predicciones_numeros TEXT,
                 predicciones_etiquetas TEXT)''')

# Verificar si las columnas 'predicciones_numeros' y 'predicciones_etiquetas' existen, y si no, agregarlas
c.execute("PRAGMA table_info(predicciones)")
columnas = [columna[1] for columna in c.fetchall()]
if 'predicciones_numeros' not in columnas:
    c.execute("ALTER TABLE predicciones ADD COLUMN predicciones_numeros TEXT")
if 'predicciones_etiquetas' not in columnas:
    c.execute("ALTER TABLE predicciones ADD COLUMN predicciones_etiquetas TEXT")
conn.commit()

# Cargar las imágenes para la introducción
imagen = Image.open('fotos/corazonreal.png')
imagen_intro = Image.open('fotos/corazon_portada.jpg')
imagen_ecg = Image.open('fotos/ecg.webp')
imagen_ecg2 = Image.open('fotos/ecg2.jpg')

# Estilos CSS personalizados para mejorar la apariencia de la aplicación
st.markdown("""
<style>
    .title-text {
        color: #2c3e50;
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle-text {
        color: #2c3e50;
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .description-text {
        color: #34495e;
        font-size: 20px;
        text-align: justify;
        margin-bottom: 30px;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }
    .btn-open-app {
        background-color: #27ae60;
        color: white;
        font-size: 20px;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
        display: block;
        margin: 20px auto;
        text-align: center;
    }
    .btn-open-app:hover {
        background-color: #219653;
    }
    .resource-link {
        color: #2980b9;
        font-size: 18px;
    }
    .resource-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Etiquetas para las predicciones
etiquetas = ['Latidos Normales', 'Latidos de Ectopia Supraventricular', 'Latidos de Ectopia Ventricular', 'Latidos de Fusión', 'Latidos Inclasificables']

# Información sobre cada etiqueta para mostrar en la sección de estadísticas
info_etiquetas = {
    'Latidos Normales': {
        'Descripción': 'Son los latidos del corazón que siguen el ritmo y la frecuencia esperada, sin irregularidades.',
        'Asociación Patológica': 'Un patrón normal de latidos no está asociado con ninguna patología específica y representa un funcionamiento saludable del corazón.'
    },
    'Latidos de Ectopia Supraventricular': {
        'Descripción': 'Son latidos prematuros que se originan en cualquier parte del corazón por encima de los ventrículos (aurículas o nodo auriculoventricular). Estos latidos ocurren antes de lo esperado en el ciclo cardíaco.',
        'Asociación Patológica': 'Fibrilación auricular, Taquicardia supraventricular (TSV), Extrasístoles auriculares.'
    },
    'Latidos de Ectopia Ventricular': {
        'Descripción': 'Son latidos prematuros que se originan en los ventrículos. Estos latidos ocurren antes de lo esperado en el ciclo cardíaco y pueden afectar el ritmo cardíaco normal.',
        'Asociación Patológica': 'Extrasístoles ventriculares (PVCs), Taquicardia ventricular, Fibrilación ventricular.'
    },
    'Latidos de Fusión': {
        'Descripción': 'Ocurren cuando un latido normal y un latido ectópico (supraventricular o ventricular) coinciden, resultando en una combinación de ambos. La morfología del latido muestra características de ambos tipos de latidos.',
        'Asociación Patológica': 'Pueden ser indicativos de una actividad ectópica subyacente y pueden observarse en contextos donde hay un ritmo ectópico significativo, como en ciertos tipos de taquicardias.'
    },
    'Latidos Inclasificables': {
        'Descripción': 'Son latidos que no se ajustan a las categorías estándar de latidos cardíacos y no pueden ser claramente identificados como normales, supraventriculares, ventriculares o de fusión.',
        'Asociación Patológica': 'La presencia de latidos inclasificables puede sugerir una disfunción eléctrica compleja o un artefacto en la grabación del electrocardiograma. Su relevancia clínica debe ser evaluada en el contexto del paciente y otros hallazgos diagnósticos.'
    }
}

def pagina_introduccion():
    """
    Esta función configura y muestra la página de introducción de la aplicación.
    Incluye una imagen, una descripción de la aplicación y enlaces a recursos adicionales.
    """
    st.markdown('<h1 class="title-text">Sistema de Monitoreo Cardíaco en Tiempo Real</h1>', unsafe_allow_html=True)
    st.image(imagen_intro, caption='Monitoreo Cardíaco', use_column_width=True)
    st.markdown("""
        <div class="description-text">
            <p>👋 Bienvenido al <b>Sistema de Monitoreo Cardíaco en Tiempo Real</b>. Esta aplicación permite la supervisión continua de la actividad cardíaca en tiempo real.</p>
            <p>Conéctate a un dispositivo de monitoreo cardíaco a través de un puerto serial, observa los datos en vivo y guarda las grabaciones para su análisis posterior.</p>
            <h3>⚙️ Funcionalidades:</h3>
            <ul>
                <li> Visualización en tiempo real de los datos de ECG.</li>
                <li> Cálculo y visualización de la frecuencia cardíaca en BPM.</li>
                <li> Grabación y almacenamiento de los datos de ECG.</li>
                <li> Predicción que clasifica cada ciclo cardíaco.</li>
                <li> Almacenamiento de las predicciones en una base de datos.</li>
            </ul>
            <h3>📋 Páginas de la Aplicación:</h3>
            <h4>Datos en Vivo:</h4>
            <p>En esta sección, puedes visualizar los datos de tu ECG en tiempo real. Sigue los pasos para configurar tu dispositivo y comenzar la monitorización:</p>
            <ol>
                <li>Selecciona el puerto COM correspondiente a tu dispositivo de monitoreo.</li>
                <li>Abre la conexión para empezar a recibir datos.</li>
                <li>Observa la gráfica del ECG en tiempo real y monitorea tu frecuencia cardíaca.</li>
                <li>Utiliza la opción de grabación para almacenar sesiones de datos para su análisis posterior.</li>
            </ol>
            <h4>Análisis de Datos:</h4>
            <p>En esta sección, puedes cargar y analizar las grabaciones de datos de ECG almacenadas. Sigue los pasos para realizar un análisis detallado:</p>
            <ol>
                <li>Carga el archivo de grabación de ECG desde tu dispositivo.</li>
                <li>Visualiza la gráfica de ECG y utiliza las herramientas disponibles para analizar los segmentos de interés.</li>
                <li>Aplica la funcionalidad de predicción para clasificar los ciclos cardíacos.</li>
                <li>Guarda los resultados del análisis y las predicciones en la base de datos para una revisión posterior.</li>
            </ol>
            <h4>Base de Datos:</h4>
            <p>En esta sección, puedes gestionar las predicciones almacenadas y revisar los registros históricos. Sigue los pasos para acceder y administrar tu base de datos:</p>
            <ol>
                <li>Visualiza los registros de predicciones almacenadas en la base de datos.</li>
                <li>Filtra los registros por fecha, etiquetas de predicción, y otros criterios relevantes.</li>
                <li>Elimina registros incorrectos o que ya no sean necesarios.</li>
                <li>Exporta los datos seleccionados para su uso en otros análisis o informes.</li>
            </ol>
            <p>Si tienes alguna duda, contacta a tu profesional de salud.</p>
        </div>
    """, unsafe_allow_html=True)

# Función para la página de datos en vivo
def pagina_datos_en_vivo():
    """
    Esta función configura y muestra la página de datos en vivo.
    Permite al usuario conectarse a un dispositivo de monitoreo cardíaco y visualizar datos en tiempo real.
    """
    st.markdown('<h1 class="title-text">Datos en Vivo</h1>', unsafe_allow_html=True)

    # Botón para abrir la ventana de monitoreo cardíaco
    st.markdown('<h2 class="subtitle-text">Abrir Ventana de Monitoreo Cardíaco</h2>', unsafe_allow_html=True)
    if st.button("Abrir Ventana Monitoreo Cardíaco", key="btn_open_app"):
        threading.Thread(target=lambda: subprocess.Popen(['python', 'serialmonitor.py'])).start()
        st.success("Ventana Monitoreo Cardíaco Iniciada. Por favor, espere un momento.")

    st.markdown("""
        <div class="description-text">
            <p>Conéctate a un dispositivo de monitoreo cardíaco y observa los datos de ECG en tiempo real. Esta sección te permitirá ver la actividad eléctrica del corazón a medida que sucede, lo cual es fundamental para la detección temprana de irregularidades y para la monitorización continua de pacientes con afecciones cardíacas.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="subtitle-text">Instrucciones de Uso</h2>', unsafe_allow_html=True)

    st.markdown("""
        <div class="description-text">
            <h3>1. Colocación de los Electrodos</h3>
            <p>Para obtener una lectura precisa, coloca los electrodos en las posiciones correctas del cuerpo del paciente. La colocación adecuada es crucial para garantizar la calidad de la señal. A continuación se muestra una guía visual:</p>
        </div>
    """, unsafe_allow_html=True)
    imagen_electrodos = Image.open('fotos/imagen.png')
    st.image(imagen_electrodos, caption='Colocación de los Electrodos', width=250)  # Ajustar el tamaño de la imagen

    st.markdown("""
        <div class="description-text">
            <h3>2. Conexión del Dispositivo</h3>
            <p>Sigue estos pasos para conectar y utilizar el dispositivo de monitoreo cardíaco:</p>
            <ol>
                <li>Conecta el dispositivo de monitoreo cardíaco al puerto USB de tu computadora.</li>
                <li>En la ventana, selecciona el puerto COM al que está conectado el electrocardiógrafo en el menú desplegable.</li>
                <li>Haz clic en "Abrir Serial" para iniciar la conexión con el dispositivo.</li>
                <li>Observa los datos de ECG en tiempo real en el gráfico proporcionado.</li>
                <li>Para iniciar la grabación de los datos, haz clic en "Iniciar Grabación".</li>
                <li>Para detener la grabación, haz clic en "Detener Grabación".</li>
                <li>Para cerrar la conexión con el dispositivo, haz clic en "Cerrar Serial".</li>
            </ol>
            <p>Nota: Asegúrate de cerrar la conexión serial antes de desconectar el dispositivo del puerto USB para evitar daños o pérdida de datos.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="description-text">
            <h3>3. Interpretación de los Datos</h3>
            <p>Una vez que la conexión esté establecida y los datos se estén mostrando, puedes interpretar las ondas del ECG para identificar diferentes características del ritmo cardíaco:</p>
            <ul>
                <li><b>Onda P:</b> Representa la despolarización auricular, que es la activación de las aurículas del corazón.</li>
                <li><b>Complejo QRS:</b> Representa la despolarización ventricular, que es la activación de los ventrículos del corazón.</li>
                <li><b>Onda T:</b> Representa la repolarización ventricular, que es la recuperación de los ventrículos después de la contracción.</li>
            </ul>
            <p>La interpretación correcta de estas ondas es crucial para el diagnóstico de diversas afecciones cardíacas. Asegúrate de consultar a un profesional de salud para un análisis detallado.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="description-text">
            <h3>4. Consejos para una Mejor Lectura</h3>
            <ul>
                <li>Evita el movimiento excesivo durante la medición para reducir el ruido en la señal.</li>
                <li>Asegúrate de que los electrodos estén firmemente adheridos a la piel.</li>
                <li>Evita lugares con interferencias electromagnéticas.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)


# Función para subir el archivo y procesar los datos
def subir_y_procesar_archivo():
    """
    Esta función permite al usuario subir un archivo Excel con datos de ECG y los procesa.

    Returns:
        new_ecg_data (DataFrame): Los datos de ECG cargados desde el archivo.
    """
    archivo_subido = st.file_uploader("Sube tu archivo Excel", type=["xls", "xlsx"])
    if archivo_subido is not None:
        try:
            nuevos_datos_ecg = pd.read_excel(archivo_subido)
            st.success("Archivo subido correctamente.")
            return nuevos_datos_ecg
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    return None

# Función para preprocesar los datos de ECG
def preprocesar_datos_ecg(nuevos_datos_ecg):
    """
    Esta función preprocesa los datos de ECG eliminando los últimos 500 datos y convierte los índices a tiempo en segundos.

    Args:
        nuevos_datos_ecg (DataFrame): Los datos de ECG cargados desde el archivo.

    Returns:
        valores_ecg (array): Valores de ECG preprocesados.
        valores_tiempo (array): Valores de tiempo en segundos.
    """
    valores_ecg = nuevos_datos_ecg.iloc[:, 1].values  # Extraer los valores de ECG
    valores_ecg = valores_ecg[:-500]  # Eliminar los últimos 500 datos
    valores_tiempo = np.arange(len(valores_ecg)) * 0.01  # 10 ms por muestra
    return valores_ecg, valores_tiempo

# Función para seleccionar la ventana de tiempo
def seleccionar_ventana_tiempo(valores_tiempo, valores_ecg):
    """
    Esta función permite al usuario seleccionar una ventana de tiempo para analizar los datos de ECG.

    Args:
        valores_tiempo (array): Valores de tiempo en segundos.
        valores_ecg (array): Valores de ECG.

    Returns:
        ventana_ecg (array): Valores de ECG en la ventana seleccionada.
        ventana_tiempo (array): Valores de tiempo en la ventana seleccionada.
    """
    st.markdown('<h2 class="subtitle-text">Selecciona la ventana de tiempo (en segundos)</h2>', unsafe_allow_html=True)
    max_tiempo = valores_tiempo[-1]
    inicio_tiempo = st.number_input('Inicio (s)', min_value=0.0, max_value=max_tiempo, value=0.0)
    fin_tiempo = st.number_input('Fin (s)', min_value=0.0, max_value=max_tiempo, value=min(60.0, max_tiempo))

    if inicio_tiempo >= fin_tiempo:
        st.error('El valor de inicio debe ser menor que el valor de fin.')
        return None, None
    else:
        muestra_inicio = int(inicio_tiempo * 100)
        muestra_fin = int(fin_tiempo * 100)
        ventana_ecg = valores_ecg[muestra_inicio:muestra_fin]
        ventana_tiempo = valores_tiempo[muestra_inicio:muestra_fin]
        return ventana_ecg, ventana_tiempo

# Función para detectar picos R en la ventana seleccionada
def detectar_picos_r(ventana_ecg, ventana_tiempo):
    """
    Esta función detecta los picos R en la ventana de tiempo seleccionada y muestra los picos detectados.

    Args:
        ventana_ecg (array): Valores de ECG en la ventana seleccionada.
        ventana_tiempo (array): Valores de tiempo en la ventana seleccionada.

    Returns:
        picos (array): Índices de los picos R detectados.
    """
    umbral_altura = 0.5  # Ajustar este parámetro según sea necesario
    umbral_distancia = 50  # Ajustar la distancia mínima en muestras (ms)
    picos, _ = find_peaks(ventana_ecg, height=umbral_altura, distance=umbral_distancia)
    
    # Mostrar los picos detectados
    plt.figure(figsize=(12, 6))
    plt.plot(ventana_tiempo, ventana_ecg, label='Señal ECG')
    plt.plot(ventana_tiempo[picos], ventana_ecg[picos], "x", label='Picos Detectados')
    plt.title('Detección de picos R')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')
    plt.legend()
    st.pyplot(plt)
    
    return picos

# Función para segmentar latidos cardíacos centrados en picos R
def segmentar_latidos(picos, ventana_ecg):
    """
    Esta función segmenta los latidos cardíacos centrados en los picos R detectados.

    Args:
        picos (array): Índices de los picos R detectados.
        ventana_ecg (array): Valores de ECG en la ventana seleccionada.

    Returns:
        segmentos_finales (list): Lista de segmentos de latidos cardíacos.
    """
    muestras_antes = 35  # Número de muestras antes del pico R
    muestras_despues = 35   # Número de muestras después del pico R
    tamano_ventana = muestras_antes + muestras_despues + 1  # Longitud total del segmento

    segmentos = []
    for pico in picos:
        inicio_seg = max(0, pico - muestras_antes)
        fin_seg = min(len(ventana_ecg), pico + muestras_despues + 1)
        segmento = ventana_ecg[inicio_seg:fin_seg]
        if len(segmento) < tamano_ventana:  # Rellenar con ceros si es necesario
            segmento = np.pad(segmento, (0, tamano_ventana - len(segmento)), 'constant')
        segmentos.append(segmento)
    
    # Rellenar cada segmento con ceros hasta alcanzar 187 muestras
    segmentos_finales = [np.pad(segmento, (0, 187 - len(segmento)), 'constant') for segmento in segmentos]
    return segmentos_finales

# Función para hacer predicciones con el modelo entrenado
def realizar_predicciones(segmentos_finales):
    """
    Esta función carga el modelo entrenado y hace predicciones en los segmentos de ECG.

    Args:
        segmentos_finales (list): Lista de segmentos de latidos cardíacos.

    Returns:
        predicciones (array): Predicciones del modelo.
        etiquetas_predicciones (list): Etiquetas de las predicciones.
    """
    modelo = joblib.load('ecg_model.pkl')
    X_nuevos = pd.DataFrame(segmentos_finales)
    predicciones = modelo.predict(X_nuevos)
    etiquetas_predicciones = [etiquetas[pred] for pred in predicciones]
    return predicciones, etiquetas_predicciones

# Función para guardar predicciones en la base de datos
def guardar_predicciones_db(predicciones, etiquetas_predicciones):
    """
    Esta función guarda las predicciones en la base de datos con la fecha y hora actuales.

    Args:
        predicciones (array): Predicciones del modelo.
        etiquetas_predicciones (list): Etiquetas de las predicciones.
    """
    fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    predicciones_numeros_str = ','.join(map(str, predicciones))
    predicciones_etiquetas_str = ','.join(etiquetas_predicciones)
    c.execute("INSERT INTO predicciones (fecha_hora, predicciones_numeros, predicciones_etiquetas) VALUES (?, ?, ?)",
              (fecha_hora_actual, predicciones_numeros_str, predicciones_etiquetas_str))
    conn.commit()
    st.success("Predicciones guardadas en la base de datos.")

# Función para mostrar los resultados de las predicciones
def mostrar_predicciones(predicciones, etiquetas_predicciones, segmentos_finales):
    """
    Esta función muestra los resultados de las predicciones en un DataFrame y permite la visualización de cada segmento.

    Args:
        predicciones (array): Predicciones del modelo.
        etiquetas_predicciones (list): Etiquetas de las predicciones.
        segmentos_finales (list): Lista de segmentos de latidos cardíacos.
    """
    resultados_df = pd.DataFrame({
        'Segmento': range(len(predicciones)),
        'Predicción (Número)': predicciones,
        'Predicción (Etiqueta)': etiquetas_predicciones
    })

    st.markdown('<h2 class="subtitle-text">Resultados de las Predicciones</h2>', unsafe_allow_html=True)
    st.dataframe(resultados_df)

    if st.button("Guardar Resultados en la Base de Datos"):
        guardar_predicciones_db(predicciones, etiquetas_predicciones)

    indice_segmento = st.slider('Selecciona el segmento', 0, len(segmentos_finales) - 1, 0)

    def graficar_segmento(indice_segmento):
        plt.figure(figsize=(12, 6))
        plt.plot(segmentos_finales[indice_segmento])
        plt.title(f'Segmento {indice_segmento} - Predicción: {predicciones[indice_segmento]} ({etiquetas_predicciones[indice_segmento]})')
        plt.xlabel('Muestras')
        plt.ylabel('Amplitud')
        st.pyplot(plt)

    graficar_segmento(indice_segmento)

# Función para mostrar información de las predicciones
def mostrar_info_predicciones():
    """
    Esta función muestra información sobre cada etiqueta de predicción.
    """
    st.markdown('<h2 class="subtitle-text">Información de las Predicciones</h2>', unsafe_allow_html=True)
    
    # Convertir el diccionario a un DataFrame para la tabla
    info_datos = {
        "Etiqueta": list(info_etiquetas.keys()),
        "Descripción": [info["Descripción"] for info in info_etiquetas.values()],
        "Asociación Patológica": [info["Asociación Patológica"] for info in info_etiquetas.values()]
    }
    info_df = pd.DataFrame(info_datos)
    
    # Mostrar la tabla en Streamlit
    st.table(info_df)

# Función para mostrar y gestionar la base de datos
def pagina_base_datos():
    """
    Esta función muestra la base de datos de predicciones y permite gestionar los registros.
    """
    st.markdown('<h1 class="title-text">Base de Datos de Predicciones</h1>', unsafe_allow_html=True)
    predicciones_db = pd.read_sql_query("SELECT id, fecha_hora, predicciones_numeros, predicciones_etiquetas FROM predicciones", conn)
    st.dataframe(predicciones_db)

    seleccion_eliminar = st.multiselect('Selecciona los IDs de las predicciones a eliminar', predicciones_db['id'].tolist())

    if st.button('Eliminar Predicciones Seleccionadas'):
        if seleccion_eliminar:
            c.executemany('DELETE FROM predicciones WHERE id=?', [(id,) for id in seleccion_eliminar])
            conn.commit()
            st.success('Predicciones eliminadas.')
            # Actualizar la visualización de la base de datos
            predicciones_db = pd.read_sql_query("SELECT id, fecha_hora, predicciones_numeros, predicciones_etiquetas FROM predicciones", conn)
            st.dataframe(predicciones_db)
        else:
            st.error('Selecciona al menos una predicción para eliminar.')

    if st.button('Descargar Base de Datos'):
        predicciones_db.to_csv('predicciones_ecg.csv', index=False)
        with open('predicciones_ecg.csv', 'rb') as file:
            st.download_button('Descargar CSV', file, file_name='predicciones_ecg.csv')

# Función para la página de análisis de datos
def pagina_analisis_datos():
    """
    Esta función configura y muestra la página de análisis de datos.
    Permite al usuario subir un archivo Excel con datos de ECG, procesarlos y mostrar los resultados de las predicciones.
    """
    st.markdown('<h1 class="title-text">Análisis de Datos</h1>', unsafe_allow_html=True)
    st.markdown("""
        <div class="description-text">
            <p>Sube un archivo de datos de ECG en formato Excel para analizarlo.</p>
        </div>
    """, unsafe_allow_html=True)

    nuevos_datos_ecg = subir_y_procesar_archivo()
    if nuevos_datos_ecg is not None:
        valores_ecg, valores_tiempo = preprocesar_datos_ecg(nuevos_datos_ecg)
        ventana_ecg, ventana_tiempo = seleccionar_ventana_tiempo(valores_tiempo, valores_ecg)
        
        if ventana_ecg is not None and ventana_tiempo is not None:
            picos = detectar_picos_r(ventana_ecg, ventana_tiempo)
            segmentos_finales = segmentar_latidos(picos, ventana_ecg)
            predicciones, etiquetas_predicciones = realizar_predicciones(segmentos_finales)
            mostrar_predicciones(predicciones, etiquetas_predicciones, segmentos_finales)
            mostrar_info_predicciones()

# Diccionario para el menú de navegación
paginas = {
    "Introducción": pagina_introduccion,
    "Datos en Vivo": pagina_datos_en_vivo,
    "Análisis de Datos": pagina_analisis_datos,
    "Base de Datos": pagina_base_datos
}

# Menú de navegación
st.sidebar.title("Navegación")
seleccion = st.sidebar.radio("Ir a", list(paginas.keys()))

# Mostrar la página seleccionada
paginas[seleccion]()

