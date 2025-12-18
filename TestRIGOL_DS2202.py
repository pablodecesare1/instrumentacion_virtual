# -*- coding: utf-8 -*-
"""
@author: Bruno

Archivo para probar la funcion medir_RC de Operador_osciloscopio.

"""
import matplotlib.pyplot as plt
# Traemos el import vxi11
import time
# Traemos el import vxi11
import vxi11
# Traemos la libreria VISA
import pyvisa as visa
# Traemos matplotlib para poder graficar
import matplotlib.pyplot as plt
# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'InstVirtualLib')
import platform
# Traemos todos los osciloscopios
from InstVirtualLib.osciloscopios import RIGOL_DS2202
# Traemos el operador
import operador

VXI11 = vxi11.Instrument("192.168.0.100")

MiOsciloscopio = RIGOL_DS2202(handler=None, VXI11=VXI11)


# Informamos el modelo del osciloscopio conectado
print("Esta conectado un %s"%MiOsciloscopio.INSTR_ID)


# Inicio de las pruebas de compatibilidad entre codigos 



X, y = MiOsciloscopio.get_trace(1)
print(len(X))
# --- PLOTEO ---
plt.figure(figsize=(10,5))
plt.plot(X, y)
plt.xlabel("Tiempo [s]")
plt.ylabel("Voltaje [V]")
plt.grid(True)
plt.tight_layout()
plt.show()

#set_chan_DIV
MiOsciloscopio.set_chan_DIV("0.1", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("0.2", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("0.4", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("0.5", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("1", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("2", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("10", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("20", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DIV("50e-3", 1)

time.sleep(1)

#set_chan_COP_DC set_chan_COP_AC set_chan_COP_GND
MiOsciloscopio.set_chan_COP_AC(1)
time.sleep(1)
MiOsciloscopio.set_chan_COP_GND(1)
time.sleep(1)
MiOsciloscopio.set_chan_COP_DC(1)

#get_chan_div
print(MiOsciloscopio.get_chan_DIV(1))

MiOsciloscopio.set_chan_OFFSET("0", 1)
time.sleep(1)
MiOsciloscopio.set_chan_DISPLAY("1", 1)

MiOsciloscopio.set_trigger_edge_slope_neg()
time.sleep(1)
MiOsciloscopio.set_trigger_edge_slope_pos()
print(MiOsciloscopio.get_trigger_edge_slope())

MiOsciloscopio.set_trigger_edge_source(1)
print(MiOsciloscopio.get_trigger_edge_source())


print(MiOsciloscopio.get_trigger_level())
MiOsciloscopio.set_trigger_level("10e-3")

MiOsciloscopio.set_BT("10e-3")
print(MiOsciloscopio.get_BT())

MiOsciloscopio.set_memdepth("140000")
print(MiOsciloscopio.get_memdepth())
print(MiOsciloscopio.get_samplerate())



MiOsciloscopio.close()

