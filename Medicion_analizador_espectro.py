import pyvisa as visa

# Traemos matplotlib para poder graficar
import matplotlib.pyplot as plt
# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'Libreria')
from instrument import Instrument
from analizador_espectro import Rigol_DSA800
import numpy as np
# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)

sys.excepthook = excepthook



USE_DEVICE = 0
# Abrimos el instrumento
#platforma = platform.platform();
#print(platforma)

rm=visa.ResourceManager('@ni')
print(rm.list_resources())


instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])

miAnalizadorDeEspectro=Rigol_DSA800(instrument_handler)

# Informamos el modelo del osciloscopio conectado
print("Esta conectado un %s"%miAnalizadorDeEspectro.INSTR_ID)


#--------------------------------------------Funciones de set----------------------------------------------------------
#miAnalizadorDeEspectro.set_freq_center(20000000) #Funciona
#miAnalizadorDeEspectro.set_freq_start(1000000) #Funciona
#miAnalizadorDeEspectro.set_freq_stop(2000000) #Funciona
#miAnalizadorDeEspectro.set_span(10000000) #Funciona
#



"""
#----------------------------------------------Ejemplo de get_trace-----------------------------------------------------
a=miAnalizadorDeEspectro.get_trace()
f=range(len(a))
plt.plot(f,a)
plt.show()
"""

#miAnalizadorDeEspectro.set_marker_freq(2,21000000)
miAnalizadorDeEspectro.set_freq_center(100000000)
miAnalizadorDeEspectro.set_span(30000000)
miAnalizadorDeEspectro.set_referencelevel(-50)
miAnalizadorDeEspectro.set_marker_delta(2)
#miAnalizadorDeEspectro.set_marker_reference_level(2)
miAnalizadorDeEspectro.set_marker_freq(2,22000000)





MiOsciloscopio.close()