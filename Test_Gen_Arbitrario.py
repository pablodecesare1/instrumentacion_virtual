# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 09:57:19 2018

@author: Ramiro
"""

# Traemos la libreria VISA
import pyvisa as visa
# Traemos matplotlib para poder graficar
import matplotlib.pyplot as plt
# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'InstVirtualLib')
import platform
# Traemos el generador
from InstVirtualLib.generadores_arbitrarios import Agilent33512A
# Siempre util numpy y scipy...
import numpy as np
from scipy import signal

# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook

# Device a utilizar de la lista
USE_DEVICE = 0

# Abrimos el instrumento con el backend correcto
platforma = platform.platform()
print(platforma)
if 'pyvisa' in sys.modules:
	rm=visa.ResourceManager('@py')
elif 'visa' in sys.modules:
	rm=visa.ResourceManager('@ni')
else:
	error()

# Instancio el instrumento
instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])
MiGenArb = Agilent33512A(instrument_handler)

# Informamos el modelo del generador conectado
print("Esta conectado un %s"%MiGenArb.INSTR_ID)

# Seteamos la señal senoidal de prueba
t,prueba = MiGenArb.senoidal()

# Mostramos la señal
plt.plot(t,prueba)
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

