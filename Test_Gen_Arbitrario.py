"""
Created on Fri Jun  1 09:57:19 2018

@author: Ramiro
"""

# Traemos la libreria VISA
# Agreamos el path de las librerias
import sys

# Traemos matplotlib para poder graficar
import matplotlib.pyplot as plt
import pyvisa as visa

sys.path.insert(0, "inst_virtual_lib")
import platform

# Siempre util numpy y scipy...
# Traemos el generador
from inst_virtual_lib.generadores_arbitrarios import Agilent33512A


# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)


sys.excepthook = excepthook

# Device a utilizar de la lista
USE_DEVICE = 0

# Abrimos el instrumento con el backend correcto
platforma = platform.platform()
print(platforma)
rm = visa.ResourceManager()

# Instancio el instrumento
instrument_handler = rm.open_resource(rm.list_resources()[USE_DEVICE])
MiGenArb = Agilent33512A(instrument_handler)

# Informamos el modelo del generador conectado
print(f"Esta conectado un {MiGenArb.INSTR_ID}")

# Seteamos la señal senoidal de prueba
t, prueba = MiGenArb.senoidal()

# Mostramos la señal
plt.plot(t, prueba)
plt.show()

# Creamos una señal aleatoria en numpy
# muestras = 10000
# MiGenArb.sampleRate = 100000
# t = np.linspace(0,muestras*1/MiGenArb.sampleRate,muestras)
# chirp = signal.chirp(t, 1e3, t[int(np.floor(muestras/2))], 2e3)
# MiGenArb.arb_signal(chirp, amp_scale = 1)

# Mostramos la señal
# plt.plot(t,chirp)
# plt.show()

MiGenArb.close()
