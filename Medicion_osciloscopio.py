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
# Traemos todos los osciloscopios
from InstVirtualLib.osciloscopios import GW_Instek
from InstVirtualLib.osciloscopios import rigol
from InstVirtualLib.osciloscopios import Tektronix_DSO_DPO_MSO_TDS
# Traemos el operador
import operador

print("1")
# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)
print("2")
sys.excepthook = excepthook
print("3")


# Seteamos el tipo de osciloscio a utilizar
OSCILOSCOPIOS = 0	# 0: GW_Instek
			# 1: rigol
			# 2: Tektronix_DSO_DPO_MSO_TDS

USE_DEVICE = -1

# Abrimos el instrumento
platforma = platform.platform()
print(platforma)
rm=visa.ResourceManager()
print("4")
instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])
print("5")
if OSCILOSCOPIOS == 0:
	print("6")
	MiOsciloscopio = GW_Instek(instrument_handler)
elif OSCILOSCOPIOS == 1:
	print("7")
	MiOsciloscopio = rigol(instrument_handler)
elif OSCILOSCOPIOS == 2:
	print("8")
	MiOsciloscopio = Tektronix_DSO_DPO_MSO_TDS(instrument_handler)
else:
	print("9")
	raise ValueError('Tipo de osciloscopio fuera de lista.')


# Informamos el modelo del osciloscopio conectado
print("Esta conectado un %s"%MiOsciloscopio.INSTR_ID)
print("10")

# Pedimos el trazo de cada canal, la salida es en ([seg.],[volt])
tiempo1,tension1=MiOsciloscopio.get_trace("1",VERBOSE=False)
#tiempo2,tension2=MiOsciloscopio.get_trace("2",VERBOSE=False)
print("11")
# Ploteamos los canales
print("PLot Momento")
plt.plot(tiempo1,tension1)
#plt.plot(,tiempo2,tension2)
plt.show()


# Generamos un operador y pedimos el valor RMS actual
operador_1 = operador.Operador_osciloscopio(MiOsciloscopio,"Workbench_I")

val_RMS = operador_1.medir_Vrms(canal = 1, VERBOSE = False)

print('Vrms = %0.5f'%val_RMS)


MiOsciloscopio.close()





