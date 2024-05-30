import streamlit as st
import webview
import threading
import subprocess

def start_tkinter_app():
    # Ejecuta la aplicación de Tkinter en un hilo separado
    subprocess.Popen(['python', 'app.py'])

st.title("Integración de Tkinter con Streamlit")

# Botón para iniciar la aplicación de Tkinter
if st.button("Abrir Aplicación Tkinter"):
    threading.Thread(target=start_tkinter_app).start()
    st.write("Aplicación Tkinter Iniciada")
