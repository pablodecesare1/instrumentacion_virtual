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

VXI11 = vxi11.Instrument("10.42.0.47")

MiOsciloscopio = RIGOL_DS2202(handler=None, VXI11=VXI11)


# Informamos el modelo del osciloscopio conectado
print("Esta conectado un %s"%MiOsciloscopio.INSTR_ID)


# Inicio de las pruebas de compatibilidad entre codigos 


#MiOsciloscopio.set_BT_Delay("10u")
#print(MiOsciloscopio.get_BT_Delay())
MiOsciloscopio.unset_BT_Vernier
MiOsciloscopio.set_BT("10e-6")
print(MiOsciloscopio.get_BT())


MiOsciloscopio.close()

