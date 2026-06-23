# Agreamos el path de las librerias
import sys

# Traemos matplotlib para poder graficar
import pyvisa as visa

sys.path.insert(0, "inst_virtual_lib")
from inst_virtual_lib.analizador_espectro import RigolDsa800


# Definimos una funcion para poder ejecutar un mensaje de error
def excepthook(type, value, traceback):
    print(value)


sys.excepthook = excepthook


USE_DEVICE = 0
# Abrimos el instrumento
# platforma = platform.platform();
# print(platforma)

rm = visa.ResourceManager()
print(rm.list_resources())


instrument_handler = rm.open_resource(rm.list_resources()[USE_DEVICE])

analizador_de_espectro = RigolDsa800(instrument_handler)

# Informamos el modelo del osciloscopio conectado
print(f"Esta conectado un {analizador_de_espectro.INSTR_ID}")


# -------------------------Funciones de set-------------------------------------
# analizador_de_espectro.set_freq_center(20000000) #Funciona
# analizador_de_espectro.set_freq_start(1000000) #Funciona
# analizador_de_espectro.set_freq_stop(2000000) #Funciona
# analizador_de_espectro.set_span(10000000) #Funciona
#


"""
#------------------------Ejemplo de get_trace-----------------------------------
a=analizador_de_espectro.get_trace()
f=range(len(a))
plt.plot(f,a)
plt.show()
"""

# analizador_de_espectro.set_marker_freq(2,21000000)
analizador_de_espectro.set_freq_center(100000000)
analizador_de_espectro.set_span(30000000)
analizador_de_espectro.set_referencelevel(-50)
analizador_de_espectro.set_marker_delta(2)
# analizador_de_espectro.set_marker_reference_level(2)
analizador_de_espectro.set_marker_freq(2, 22000000)


analizador_de_espectro.close()
