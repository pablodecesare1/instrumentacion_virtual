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
sys.path.insert(0, 'Librerias')
# Traemos todos los osciloscopios
from osciloscopios import GW_Instek, rigol, Tektronix_DSO_DPO_MSO_TDS

# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook



# Seteamos el tipo de osciloscio a utilizar
OSCILOSCOPIOS = 0	# 0: GW_Instek
			# 1: rigol
			# 2: Tektronix_DSO_DPO_MSO_TDS


# Abrimos el instrumento
rm=visa.ResourceManager()
instrument_handler=rm.open_resource(rm.list_resources()[0])

if OSCILOSCOPIOS == 0:
	MiOsciloscopio = GW_Instek(instrument_handler)
elif OSCILOSCOPIOS == 1:
	MiOsciloscopio = rigol(instrument_handler)
elif OSCILOSCOPIOS == 2:
	MiOsciloscopio = Tektronix_DSO_DPO_MSO_TDS(instrument_handler)
else:
	raise ValueError('Tipo de osciloscopio fuera de lista.')


# Informamos el modelo del osciloscopio conectado
print("Esta conectado un {}".format(MiOsciloscopio.print_ID))


# Pedimos el trazo de cada canal, la salida es en ([seg.],[volt])
tiempo1,tension1=MiOsciloscopio.get_trace("1")
tiempo2,tension2=MiOsciloscopio.get_trace("2")

# Ploteamos los canales
plt.plot(tiempo1,tension1,tiempo2,tension2)


# Generamos un operador y pedimos el valor RMS actual
operador_1 = Operador(MiOsciloscopio,"Workbench_I")

val_RMS = medir_Vrms(canal = 1, VERBOSE = True)

print('Vrms = %0.5f'%val_RMS)





