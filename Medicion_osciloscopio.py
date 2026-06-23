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

# Traemos el operador
import operador

# Traemos todos los osciloscopios
from inst_virtual_lib.osciloscopios import GwInstek, Rigol, TektronixDsoDpoMsoTds


# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)


sys.excepthook = excepthook


# Seteamos el tipo de osciloscio a utilizar
OSCILOSCOPIOS = 0  # 0: GwInstek
# 1: Rigol
# 2: TektronixDsoDpoMsoTds

USE_DEVICE = -1

# Abrimos el instrumento
platforma = platform.platform()
print(platforma)
rm = visa.ResourceManager()
instrument_handler = rm.open_resource(rm.list_resources()[USE_DEVICE])
if OSCILOSCOPIOS == 0:
    MiOsciloscopio = GwInstek(instrument_handler)
elif OSCILOSCOPIOS == 1:
    MiOsciloscopio = Rigol(instrument_handler)
elif OSCILOSCOPIOS == 2:
    MiOsciloscopio = TektronixDsoDpoMsoTds(instrument_handler)
else:
    raise ValueError("Tipo de osciloscopio fuera de lista.")


# Informamos el modelo del osciloscopio conectado
print(f"Esta conectado un {MiOsciloscopio.INSTR_ID}")

# Pedimos el trazo de cada canal, la salida es en ([seg.],[volt])
tiempo1, tension1 = MiOsciloscopio.get_trace("1", verbose=False)
# tiempo2,tension2=MiOsciloscopio.get_trace("2",verbose=False)
# Ploteamos los canales
plt.plot(tiempo1, tension1)
# plt.plot(,tiempo2,tension2)
plt.show()


# Generamos un operador y pedimos el valor RMS actual
operador_1 = operador.OperadorOsciloscopio(MiOsciloscopio, "Workbench_I")

VAL_RMS = operador_1.medir_vrms(canal=1, verbose=False)

print(f"Vrms = {VAL_RMS:0.5f}")


MiOsciloscopio.close()
