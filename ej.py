import tkinter as tk
from tkinter import ttk 
import matplotlib.animation as animation
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
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
    global serialAbierto
    global datosSerial
    global datosSerialGrabados
    print('bucle iniciado')
    while serialAbierto:
        try:
            lectura = float(ser.readline().strip())
            datosSerial.append(lectura)
            datosSerial.pop(0)

            if grabando:
                datosSerialGrabados.append(lectura)
        except:
            pass

def iniciarSerial():
    try:
        s = var.get()
        global ser
        ser = serial.Serial('COM' + s, 9600, timeout=20)
        ser.close()
        ser.open()
        global serialAbierto
        serialAbierto = True
        global hilo
        hilo = threading.Thread(target=leer_del_puerto, args=(ser,))
        hilo.start()
        textoConexion.set("Conectado a COM" + s)
        etiquetaConexion.config(fg="green")
        return serialAbierto
    except SerialException:
        textoConexion.set("Error: puerto incorrecto?")
        etiquetaConexion.config(fg="red")

def matar_Serial():
    try:
        global ser
        global serialAbierto
        serialAbierto = False
        time.sleep(1)
        ser.close()
        textoConexion.set("No conectado")
        etiquetaConexion.config(fg="red")
        print('serial cerrado')
    except:
        textoConexion.set("Fallo al terminar la conexión serial")

def animar(i):
    global datosSerial
    global ultima_actualizacion_bpm
    ax.clear()
    datos = datosSerial[-600:] if len(datosSerial) > 600 else datosSerial
    x = np.arange(len(datos))
    ax.plot(x, datos)

    # Calcular y mostrar BPM cada 3 segundos
    tiempo_actual = time.time()
    if tiempo_actual - ultima_actualizacion_bpm >= 3:
        if len(datos) > frecuencia_muestreo * 5:  # Asegúrate de tener al menos 5 segundos de datos
            valores_5s = datos[-frecuencia_muestreo * 5:]
            picos = detectar_picos(valores_5s, distance=frecuencia_muestreo//2, threshold=np.mean(valores_5s))
            bpm = calcular_bpm(picos, frecuencia_muestreo)
            textoBPM.set(f"BPM: {bpm}")
            ultima_actualizacion_bpm = tiempo_actual

def iniciarGrabacion():
    global grabando
    if serialAbierto:
        grabando = True
        textoGrabacion.set("Grabando . . . ")
        etiquetaGrabacion.config(fg="red")
    else:
        messagebox.showinfo("Error", "Por favor inicia el monitor serial")

def detenerGrabacion():
    global grabando
    global datosSerialGrabados
    if grabando:
        grabando = False
        textoGrabacion.set("No grabando")
        etiquetaGrabacion.config(fg="black")
        procesarGrabacion(datosSerialGrabados)
        datosSerialGrabados = []
    else:
        messagebox.showinfo("Error", "No estabas grabando!")

def procesarGrabacion(datos):
    z = scipy.signal.savgol_filter(datos, 11, 3)
    datos2 = np.asarray(z, dtype=np.float32)
    a = len(datos)
    base = peakutils.baseline(datos2, 2)
    y = datos2 - base
    directorio = tk.filedialog.asksaveasfilename(defaultextension=".xls", filetypes=(("Hoja Excel", "*.xls"),("Todos los archivos", "*.*")))
    if directorio is None:
        return
    libro = xlwt.Workbook(encoding="utf-8")
    hoja1 = libro.add_sheet("Hoja 1")
    for i in range(a):
        hoja1.write(i, 0, i)
        hoja1.write(i, 1, y[i])
    libro.save(directorio)

def detectar_picos(senal_ecg, distance=50, threshold=0.5):
    picos, _ = find_peaks(senal_ecg, distance=distance, height=threshold)
    return picos

def calcular_bpm(picos, frecuencia_muestreo):
    if len(picos) < 2:
        return 0
    intervalos_picos = np.diff(picos) / frecuencia_muestreo
    bpm = 60 / np.mean(intervalos_picos)
    return int(round(bpm))

ventana = tk.Tk()
ventana.title("Monitoreo Cardiaco en Tiempo Real")
ventana.rowconfigure(0, minsize=800, weight=1)
ventana.columnconfigure(1, minsize=800, weight=1)

fig = Figure(figsize=(6, 5), dpi=50)
ax = fig.add_subplot(1, 1, 1)
ax.set_xlim([0, 30])
ax.set_ylim([0, 150])

canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.draw()

lbl_vivo = tk.Label(text="Datos en Vivo:", font=('Helvetica', 12), fg='red')
fr_botones = tk.Frame(ventana, relief=tk.RAISED, bd=2)

textoConexion = tk.StringVar(ventana)
textoConexion.set("No conectado")
etiquetaConexion = tk.Label(fr_botones, textvariable=textoConexion, font=('Helvetica', 12), fg='red')
etiquetaConexion.grid(row=0, column=0, sticky="ew", padx=10)

var = tk.StringVar(ventana)
var.set(listaPuertos[0])
opt_com = tk.OptionMenu(fr_botones, var, *listaPuertos)
opt_com.config(width=20)
opt_com.grid(row=1, column=0, sticky="ew", padx=10)

btn_iniciar_serial = tk.Button(fr_botones, text="Abrir Serial", command=iniciarSerial)
btn_iniciar_serial.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

btn_detener_serial = tk.Button(fr_botones, text="Cerrar Serial", command=matar_Serial)
btn_detener_serial.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

textoGrabacion = tk.StringVar(ventana)
textoGrabacion.set("No grabando")
etiquetaGrabacion = tk.Label(fr_botones, textvariable=textoGrabacion, font=('Helvetica', 12), fg='black')
etiquetaGrabacion.grid(row=4, column=0, sticky="ew", padx=10)

btn_iniciar_grab = tk.Button(fr_botones, text="Iniciar Grabación", command=iniciarGrabacion)
btn_iniciar_grab.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

btn_detener_grab = tk.Button(fr_botones, text="Detener Grabación", command=detenerGrabacion)
btn_detener_grab.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

textoBPM = tk.StringVar(ventana)
textoBPM.set("BPM: N/A")
etiquetaBPM = tk.Label(fr_botones, textvariable=textoBPM, font=('Helvetica', 12), fg='blue')
etiquetaBPM.grid(row=7, column=0, sticky="ew", padx=10)

fr_botones.grid(row=0, column=0, sticky="ns")
lbl_vivo.grid(row=1, column=1, sticky="nsew")
canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

def preguntar_salir():
    if tk.messagebox.askokcancel("Cerrar", "Cerrando conexión serial"):
        matar_Serial()
        ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", preguntar_salir)
ani = animation.FuncAnimation(fig, animar, interval=100)
ventana.mainloop()

