# -*- coding: utf-8 -*-
"""
@author: Bruno

Archivo para probar la funcion medir_RC de Operador_osciloscopio.

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

# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook


# Seteamos el tipo de osciloscio a utilizar
OSCILOSCOPIOS = 0	# 0: GW_Instek
			# 1: rigol
			# 2: Tektronix_DSO_DPO_MSO_TDS

USE_DEVICE = 0


# Abrimos el instrumento
platforma = platform.platform()
print(platforma)
rm=visa.ResourceManager()


instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])

if OSCILOSCOPIOS == 0:
	MiOsciloscopio = GW_Instek(instrument_handler)
elif OSCILOSCOPIOS == 1:
	MiOsciloscopio = rigol(instrument_handler)
elif OSCILOSCOPIOS == 2:
	MiOsciloscopio = Tektronix_DSO_DPO_MSO_TDS(instrument_handler)
else:
	raise ValueError('Tipo de osciloscopio fuera de lista.')



# Informamos el modelo del osciloscopio conectado
print("Esta conectado un %s"%MiOsciloscopio.INSTR_ID)


# Generamos un operador y pedimos el valor RMS actual
operador_1 = operador.Operador_osciloscopio(MiOsciloscopio,"Workbench_I")

print("Ingrese valor de R en ohms:")

R = float(input())

print("Midiendo por metodo FFT...")
C_nF = 1e9*operador_1.medir_RC(R, "1", "2", "FFT")
print('C = %0.5fnF'%C_nF)

print("Midiendo por metodo Potencia...")
C_nF = 1e9*operador_1.medir_RC(R, "1", "2", "Potencia")
print('C = %0.5fnF'%C_nF)

print("Midiendo por metodo Lissajous...")
C_nF = 1e9*operador_1.medir_RC(R, "1", "2", "Lissajous")
print('C = %0.5fnF'%C_nF)

print("Midiendo por metodo Tiempo..")
C_nF = 1e9*operador_1.medir_RC(R, "1", "2", "Tiempo")
print('C = %0.5fnF'%C_nF)


MiOsciloscopio.close()





