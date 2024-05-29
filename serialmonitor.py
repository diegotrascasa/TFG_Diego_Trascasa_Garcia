import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import threading
import serial
from serial import SerialException
from scipy.signal import find_peaks
import scipy.signal
import peakutils

# Variables globales
recording = False
serialDataRecorded = []
serialOpen = False
ser = None

sampling_rate = 100  # Frecuencia de muestreo en Hz (100 muestras por segundo)
serialData = [0] * 6000
last_bpm_update = 0  # Tiempo del último cálculo de BPM

# Funciones para manejo del puerto serial
def read_from_port():
    global serialOpen, serialData, serialDataRecorded
    while serialOpen:
        try:
            reading = float(ser.readline().strip())
            serialData.append(reading)
            serialData.pop(0)

            if recording:
                serialDataRecorded.append(reading)
        except:
            pass

def startSerial(port):
    global ser, serialOpen
    try:
        ser = serial.Serial(port, 9600, timeout=20)
        ser.close()
        ser.open()
        serialOpen = True
        thread = threading.Thread(target=read_from_port)
        thread.start()
        return True
    except SerialException:
        return False

def kill_Serial():
    global ser, serialOpen
    try:
        serialOpen = False
        time.sleep(1)
        ser.close()
    except:
        pass

# Funciones de procesamiento de datos
def detect_peaks(ecg_signal, distance=50, threshold=0.5):
    peaks, _ = find_peaks(ecg_signal, distance=distance, height=threshold)
    return peaks

def calculate_bpm(peaks, sampling_rate):
    if len(peaks) < 2:
        return 0
    peak_intervals = np.diff(peaks) / sampling_rate
    bpm = 60 / np.mean(peak_intervals)
    return int(round(bpm))

def processRecording(data):
    z = scipy.signal.savgol_filter(data, 11, 3)
    data2 = np.asarray(z, dtype=np.float32)
    base = peakutils.baseline(data2, 2)
    y = data2 - base
    return y

# Interfaz de usuario con Streamlit
st.title("Monitoreo Cardiaco en Tiempo Real")

port = st.selectbox("Selecciona el puerto COM:", ["Selecciona el puerto COM:", "COM0", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7"])

if port != "Selecciona el puerto COM:":
    if st.button("Open Serial"):
        if startSerial(port):
            st.success(f"Conectado a {port}")
        else:
            st.error("Error: wrong port?")

if st.button("Close Serial"):
    kill_Serial()
    st.info("Not connected")

if st.button("Start Recording"):
    if serialOpen:
        global recording
        recording = True
        st.warning("Recording . . . ")
    else:
        st.error("Please start the serial monitor")

if st.button("Stop Recording"):
    global recording, serialDataRecorded
    if recording:
        recording = False
        st.info("Not Recording")
        processed_data = processRecording(serialDataRecorded)
        df = pd.DataFrame(processed_data, columns=["Filtered Data"])
        st.download_button(
            label="Download data as CSV",
            data=df.to_csv().encode('utf-8'),
            file_name='recorded_data.csv',
            mime='text/csv',
        )
        serialDataRecorded = []
    else:
        st.error("You weren't recording!")

# Gráfico en tiempo real
fig, ax = plt.subplots()
data = serialData[-600:] if len(serialData) > 600 else serialData
x = np.arange(len(data))
ax.plot(x, data)

# Calcular y mostrar BPM cada 3 segundos
current_time = time.time()
if current_time - last_bpm_update >= 3:
    if len(data) > sampling_rate * 5:  # Asegúrate de tener al menos 5 segundos de datos
        values_5s = data[-sampling_rate * 5:]
        peaks = detect_peaks(values_5s, distance=sampling_rate // 2, threshold=np.mean(values_5s))
        bpm = calculate_bpm(peaks, sampling_rate)
        st.write(f"BPM: {bpm}")
        last_bpm_update = current_time

st.pyplot(fig)
