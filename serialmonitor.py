#### IMPORTS #####

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.animation as animation
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import scipy.signal
import serial
from serial import SerialException
import peakutils
import xlwt
import threading
import time
from scipy.signal import find_peaks

# Variables globales
grabando = False
datosSerialGrabados = []
serialAbierto = False
global ser

listaPuertos = ["Selecciona el puerto COM:", "0", "1", "2", "3", "4", "5", "6", "7"]
conectado = False
datosSerial = [0] * 6000
frecuencia_muestreo = 100  # Frecuencia de muestreo en Hz (100 muestras por segundo)
ultima_actualizacion_bpm = 0  # Tiempo del último cálculo de BPM

def leer_del_puerto(ser):
    """
    Función para leer datos del puerto serial.

    Args:
        ser: Objeto serial que representa la conexión al puerto.

    Returns:
        None
    """
    global serialAbierto  # Variable global para indicar si el puerto está abierto
    global datosSerial  # Lista para almacenar los datos leídos del puerto serial
    global datosSerialGrabados  # Lista global para almacenar los datos leídos del puerto serial cuando se está grabando
    print('bucle iniciado')  # Mensaje de inicio del bucle

    # Bucle principal para leer continuamente del puerto serial mientras esté abierto
    while serialAbierto:
        try:
            # Lee una línea del puerto serial, elimina espacios en blanco y convierte a float
            lectura = float(ser.readline().strip())

            # Agrega la lectura a la lista de datos serial y elimina el primer elemento si la lista supera un cierto tamaño
            datosSerial.append(lectura)
            datosSerial.pop(0)

            # Si la grabación está activa, agrega la lectura a la lista de datos grabados
            if grabando:
                datosSerialGrabados.append(lectura)
        except:
            # Maneja cualquier excepción ocurrida durante la lectura sin interrumpir el bucle
            pass


def iniciarSerial():
    """
    Función para iniciar la conexión serial.

    Returns:
        bool: True si la conexión se realiza con éxito, False en caso contrario.
    """
    try:
        s = var.get()  # Obtiene el número de puerto desde la variable 'var'
        global ser  # Declara 'ser' como una variable global
        ser = serial.Serial('COM' + s, 9600, timeout=20)  # Inicializa el objeto Serial con el número de puerto y la velocidad de baudios
        ser.close()  # Cierra la conexión serial si está abierta
        ser.open()  # Abre la conexión serial
        global serialAbierto  # Declara 'serialAbierto' como una variable global
        serialAbierto = True  # Establece 'serialAbierto' como True para indicar que el puerto está abierto
        global hilo  # Declara 'hilo' como una variable global
        hilo = threading.Thread(target=leer_del_puerto, args=(ser,))  # Crea un hilo para leer del puerto serial
        hilo.start()  # Inicia el hilo
        textoConexion.set("Conectado a COM" + s)  # Actualiza el texto de la conexión
        etiquetaConexion.config(fg="green")  # Configura el color de la etiqueta de conexión como verde
        return serialAbierto  # Devuelve True para indicar que la conexión se realizó con éxito
    except SerialException:
        textoConexion.set("Error: puerto incorrecto?")  # Actualiza el texto de la conexión en caso de error
        etiquetaConexion.config(fg="red")  # Configura el color de la etiqueta de conexión como rojo


def kill_Serial():
    """
    Función para cerrar la conexión serial.

    Returns:
        None
    """
    try:
        global ser  # Declara 'ser' como una variable global
        global serialAbierto  # Declara 'serialAbierto' como una variable global
        serialAbierto = False  # Establece 'serialAbierto' como False para indicar que el puerto ya no está abierto
        time.sleep(1)  # Espera 1 segundo
        ser.close()  # Cierra la conexión serial
        textoConexion.set("No conectado")  # Actualiza el texto de la conexión
        etiquetaConexion.config(fg="red")  # Configura el color de la etiqueta de conexión como rojo
        print('serial cerrado')  # Imprime un mensaje indicando que la conexión serial se ha cerrado correctamente
    except:
        textoConexion.set("Fallo al terminar la conexión serial")  # Actualiza el texto de la conexión en caso de error durante el cierre


def animar(i):
    """
    Función para animar el gráfico con los datos recibidos del puerto serial.

    Args:
        i: Índice de la animación.

    Returns:
        None
    """
    global datosSerial  # Declara 'datosSerial' como una variable global
    global ultima_actualizacion_bpm  # Declara 'ultima_actualizacion_bpm' como una variable global
    ax.clear()  # Limpia el eje actual

    # Obtiene los últimos 600 datos o todos los datos si hay menos de 600
    datos = datosSerial[-600:] if len(datosSerial) > 600 else datosSerial
    x = np.arange(len(datos))  # Genera un arreglo de índices para los datos

    # Grafica los datos
    ax.plot(x, datos)

    # Calcula y muestra el BPM cada 3 segundos
    tiempo_actual = time.time()  # Obtiene el tiempo actual
    if tiempo_actual - ultima_actualizacion_bpm >= 3:  # Comprueba si ha pasado al menos 3 segundos desde la última actualización del BPM
        if len(datos) > frecuencia_muestreo * 5:  # Asegura tener al menos 5 segundos de datos (frecuencia_muestreo * 5)
            valores_5s = datos[-frecuencia_muestreo * 5:]  # Obtiene los últimos 5 segundos de datos
            picos = detectar_picos(valores_5s, distance=frecuencia_muestreo//2, threshold=np.mean(valores_5s))  # Detecta los picos en los últimos 5 segundos de datos
            bpm = calcular_bpm(picos, frecuencia_muestreo)  # Calcula el BPM basado en los picos detectados y la frecuencia de muestreo
            textoBPM.set(f"BPM: {bpm}")  # Actualiza el texto del BPM en la interfaz gráfica
            ultima_actualizacion_bpm = tiempo_actual  # Actualiza el tiempo de la última actualización del BPM con el tiempo actual


def iniciarGrabacion():
    """
    Función para iniciar la grabación de datos del puerto serial.

    Returns:
        None
    """
    global grabando  # Declara 'grabando' como una variable global
    if serialAbierto:  # Comprueba si el puerto serial está abierto
        grabando = True  # Establece 'grabando' como True para indicar que la grabación ha comenzado
        textoGrabacion.set("Grabando . . . ")  # Actualiza el texto de estado de grabación
        etiquetaGrabacion.config(fg="red")  # Configura el color de la etiqueta de grabación como rojo
    else:
        messagebox.showinfo("Error", "Por favor inicia el monitor serial")  # Muestra un mensaje de error si el puerto serial no está abierto

def detenerGrabacion():
    """
    Función para detener la grabación de datos del puerto serial.

    Returns:
        None
    """
    global grabando  # Declara 'grabando' como una variable global
    global datosSerialGrabados  # Declara 'datosSerialGrabados' como una variable global
    if grabando:  # Comprueba si se está grabando
        grabando = False  # Establece 'grabando' como False para indicar que la grabación ha terminado
        textoGrabacion.set("No grabando")  # Actualiza el texto de estado de grabación
        etiquetaGrabacion.config(fg="black")  # Configura el color de la etiqueta de grabación como negro
        procesarGrabacion(datosSerialGrabados)  # Procesa los datos grabados
        datosSerialGrabados = []  # Reinicia la lista de datos grabados
    else:
        messagebox.showinfo("Error", "No estabas grabando!")  # Muestra un mensaje de error si no se estaba grabando


def procesarGrabacion(datos):
    """
    Función para procesar los datos grabados del puerto serial.

    Args:
        datos: Lista de datos grabados.

    Returns:
        None
    """
    # Aplica un filtro de Sav-Gol a los datos
    z = scipy.signal.savgol_filter(datos, 11, 3)
    datos2 = np.asarray(z, dtype=np.float32)

    # Obtiene la longitud de los datos
    a = len(datos)

    # Calcula la línea de base de los datos filtrados
    base = peakutils.baseline(datos2, 2)

    # Calcula la señal corregida restando la línea de base a los datos filtrados
    y = datos2 - base

    # Solicita al usuario un directorio para guardar los datos procesados en un archivo Excel
    directorio = filedialog.asksaveasfilename(defaultextension=".xls", filetypes=(("Hoja Excel", "*.xls"),("Todos los archivos", "*.*")))
    if directorio is None:  # Si el usuario cancela, salir de la función
        return

    # Crea un nuevo Excel y una hoja
    libro = xlwt.Workbook(encoding="utf-8")
    hoja1 = libro.add_sheet("Hoja 1")

    # Escribe los datos procesados en la hoja de Excel
    for i in range(a):
        hoja1.write(i, 0, i)  # Escribir el índice en la primera columna
        hoja1.write(i, 1, y[i])  # Escribir el dato procesado en la segunda columna

    # Guarda el Excel en el directorio que queramos
    libro.save(directorio)


def detectar_picos(senal_ecg, distance=50, threshold=0.5):
    """
    Función para detectar los picos en una señal ECG.

    Args:
        senal_ecg: Señal ECG.
        distance: Distancia mínima entre picos.
        threshold: Umbral para considerar un pico.

    Returns:
        Array: Índices de los picos detectados.
    """
    picos, _ = find_peaks(senal_ecg, distance=distance, height=threshold)
    return picos


def calcular_bpm(picos, frecuencia_muestreo):
    """
    Función para calcular el ritmo cardíaco (BPM) a partir de los picos detectados en una señal ECG.

    Args:
        picos: Índices de los picos en la señal.
        frecuencia_muestreo: Frecuencia de muestreo de la señal.

    Returns:
        int: Ritmo cardíaco en latidos por minuto (BPM).
    """
    if len(picos) < 2:  # Si hay menos de dos picos, retorna 0
        return 0
    intervalos_picos = np.diff(picos) / frecuencia_muestreo  # Calcula los intervalos entre picos
    bpm = 60 / np.mean(intervalos_picos)  # Calcula el ritmo cardíaco promedio en BPM
    return int(round(bpm))  # Retorna el BPM redondeado a un número entero


# Crea una ventana de la interfaz gráfica
ventana = tk.Tk()
# Establece el título de la ventana
ventana.title("Monitoreo Cardiaco en Tiempo Real")
# Configura la fila 0 de la ventana para que tenga un tamaño mínimo de 800
ventana.rowconfigure(0, minsize=800, weight=1)
# Configura la columna 1 de la ventana para que tenga un tamaño mínimo de 800
ventana.columnconfigure(1, minsize=800, weight=1)

# Crea una figura para el gráfico con un tamaño específico
fig = Figure(figsize=(6, 5), dpi=50)
# Añade un subplot a la figura
ax = fig.add_subplot(1, 1, 1)
# Establece los límites de los ejes x e y del subplot
ax.set_xlim([0, 30])
ax.set_ylim([0, 150])

# Crea un lienzo para mostrar la figura dentro de la ventana
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.draw()

# Crea una etiqueta para mostrar "Datos en Vivo"
lbl_vivo = tk.Label(text="Datos en Vivo:", font=('Helvetica', 12), fg='red')
# Crea un marco para contener los botones y otras etiquetas
fr_botones = tk.Frame(ventana, relief=tk.RAISED, bd=2)

# Crea una variable de cadena para almacenar el estado de la conexión
textoConexion = tk.StringVar(ventana)
textoConexion.set("No conectado")
# Crea una etiqueta para mostrar el estado de la conexión
etiquetaConexion = tk.Label(fr_botones, textvariable=textoConexion, font=('Helvetica', 12), fg='red')
etiquetaConexion.grid(row=0, column=0, sticky="ew", padx=10)

# Crea una variable de cadena para almacenar el puerto seleccionado
var = tk.StringVar(ventana)
var.set(listaPuertos[0])

# Crea un menú desplegable para seleccionar el puerto
opt_com = tk.OptionMenu(fr_botones, var, *listaPuertos)
opt_com.config(width=20)
opt_com.grid(row=1, column=0, sticky="ew", padx=10)

# Crea un botón para abrir la conexión serial
btn_iniciar_serial = tk.Button(fr_botones, text="Abrir Serial", command=iniciarSerial)
btn_iniciar_serial.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

# Crea un botón para cerrar la conexión serial
btn_detener_serial = tk.Button(fr_botones, text="Cerrar Serial", command=kill_Serial)
btn_detener_serial.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

# Crea una variable de cadena para mostrar el estado de la grabación
textoGrabacion = tk.StringVar(ventana)
textoGrabacion.set("No grabando")
# Crea una etiqueta para mostrar el estado de la grabación
etiquetaGrabacion = tk.Label(fr_botones, textvariable=textoGrabacion, font=('Helvetica', 12), fg='black')
etiquetaGrabacion.grid(row=4, column=0, sticky="ew", padx=10)

# Crea un botón para iniciar la grabación de datos
btn_iniciar_grab = tk.Button(fr_botones, text="Iniciar Grabación", command=iniciarGrabacion)
btn_iniciar_grab.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

# Crea un botón para detener la grabación de datos
btn_detener_grab = tk.Button(fr_botones, text="Detener Grabación", command=detenerGrabacion)
btn_detener_grab.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

# Crea una variable de cadena para mostrar el BPM
textoBPM = tk.StringVar(ventana)
textoBPM.set("BPM: N/A")
# Crea una etiqueta para mostrar el BPM
etiquetaBPM = tk.Label(fr_botones, textvariable=textoBPM, font=('Helvetica', 12), fg='blue')
etiquetaBPM.grid(row=7, column=0, sticky="ew", padx=10)

# Ubica el marco de botones en la columna 0 (izquierda) y la etiqueta de "Datos en Vivo" en la columna 1
fr_botones.grid(row=0, column=0, sticky="ns")
lbl_vivo.grid(row=1, column=1, sticky="nsew")
# Colocar el gráfico en la columna 1
canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

def preguntar_salir():
    """
    Función que se ejecuta cuando se intenta cerrar la ventana principal.

    Se muestra un cuadro de diálogo de confirmación para cerrar la ventana.
    Si el usuario confirma, se cierra la conexión serial y se destruye la ventana.

    Returns:
        None
    """
    if tk.messagebox.askokcancel("Cerrar", "Cerrando conexión serial"):
        kill_Serial()  # Cierra la conexión serial
        ventana.destroy()  # Destruye la ventana principal

# Asigna la función 'preguntar_salir' al evento de cerrar la ventana
ventana.protocol("WM_DELETE_WINDOW", preguntar_salir)

# Crea una animación que actualiza el gráfico y entra en el bucle principal de la interfaz gráfica
ani = animation.FuncAnimation(fig, animar, interval=100)
ventana.mainloop()
