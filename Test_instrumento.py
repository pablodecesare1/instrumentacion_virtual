# Traemos la libreria VISA
import pyvisa as visa

# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'InstVirtualLib')
# Traemos la clase base que implmenta las funciones de VISA
from InstVirtualLib.instrument import Instrument as Instrument
from InstVirtualLib.osciloscopios import SDS2102
from InstVirtualLib.generadores_arbitrarios import Siglent1032X
import platform
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
from scipy.signal import windows
# Agregamos funcionalidades
import time


# Pedimos la lista de instrumentos
platforma = platform.platform()
print(platforma)


print("Inicializando instrumentos Siglent...")
USE_DEVICE1 = 0
USE_DEVICE2 = 1
# Pedimos la lista de instrumentos
platforma = platform.platform()
print(platforma)
rm1=visa.ResourceManager()
#rm2=visa.ResourceManager()

##Cambiar por apertura por IP de osciloscopio y Generador en un futuro
instrument_handler1=rm1.open_resource("TCPIP::192.168.0.100::2050::INSTR")
#instrument_handler2=rm2.open_resource("TCPIP::::5025::INSTR")
instrument_handler1.query("IDN?")

MiOsciloscopio.close()
#plt.figure()
#plt.plot(tiempo,tension)
#plt.grid