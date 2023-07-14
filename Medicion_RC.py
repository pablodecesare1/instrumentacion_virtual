# -*- coding: utf-8 -*-
"""
Created on Fri Jun  30 09:57:19 2023

@author: Santiago
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

plt.close('all')

# Seteamos el tipo de osciloscio a utilizar
OSCILOSCOPIOS = 0	# 0: GW_Instek
        			# 1: Rigol
			        # 2: Tektronix_DSO_DPO_MSO_TDS

USE_DEVICE = 0


# Abrimos el instrumento
platforma = platform.platform()
print(platforma)
rm=visa.ResourceManager()
# El handle puede controlar osciloscopios, analizadores, etc.
# Es generico
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

# Pedimos el trazo de cada canal, la salida es en ([seg.],[volt])
# BUG!!! si no se agrega el VERBOSE=False no anda el GW Instek
print('-------------')
tiempo1,tension1=MiOsciloscopio.get_trace("1",VERBOSE=False)
print('-------------')
tiempo2,tension2=MiOsciloscopio.get_trace("2",VERBOSE=False)
print('-------------')

# Ploteamos los canales
fig_RC= plt.figure(2)
ax_RC, ax_R= fig_RC.subplots(2)

fig_RC.sca(ax_RC)
ax_RC.plot(tiempo1,tension1, label='Tension sobre RC')
plt.legend()
fig_RC.sca(ax_R)
ax_R.plot(tiempo2,tension2, color='red', label='Tension sobre R')
plt.legend()
plt.show()

# Generamos un operador
operador_1 = operador.Operador_osciloscopio(MiOsciloscopio,"Workbench_I")

valor_cap= operador_1.medir_RC(1200, 1, 2, "POT")

print('Valor del capacitor = %f'%(valor_cap*10**9),'nF')


MiOsciloscopio.close()




