"""
@author: Bruno

Archivo para probar la funcion medir_RC de Operador_osciloscopio.

"""

# Traemos la libreria VISA
# Agreamos el path de las librerias
import sys

# Traemos matplotlib para poder graficar
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


# Generamos un operador y pedimos el valor RMS actual
operador_1 = operador.OperadorOsciloscopio(MiOsciloscopio, "Workbench_I")

print("Ingrese valor de r en ohms:")

r = float(input())

print("Midiendo por metodo FFT...")
C_nF = 1e9 * operador_1.medir_rc(r, "1", "2", "FFT")
print(f"C = {C_nF:0.5f}nF")

print("Midiendo por metodo Potencia...")
C_nF = 1e9 * operador_1.medir_rc(r, "1", "2", "Potencia")
print(f"C = {C_nF:0.5f}nF")

print("Midiendo por metodo Lissajous...")
C_nF = 1e9 * operador_1.medir_rc(r, "1", "2", "Lissajous")
print(f"C = {C_nF:0.5f}nF")

print("Midiendo por metodo Tiempo..")
C_nF = 1e9 * operador_1.medir_rc(r, "1", "2", "Tiempo")
print(f"C = {C_nF:0.5f}nF")


MiOsciloscopio.close()
