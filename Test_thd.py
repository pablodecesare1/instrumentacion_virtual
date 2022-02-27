# Script que realiza una medición de THD.

import sys
sys.path.insert(0, 'InstVirtualLib')
import matplotlib.pyplot as plt
import pyvisa as visa
import platform
from InstVirtualLib.osciloscopios import GW_Instek
from InstVirtualLib.osciloscopios import rigol
from InstVirtualLib.osciloscopios import Tektronix_DSO_DPO_MSO_TDS
from InstVirtualLib.operador import Operador_osciloscopio

# Seteamos el tipo de osciloscio a utilizar
OSCILOSCOPIOS = 0	# 0: GW_Instek
			# 1: rigol
			# 2: Tektronix_DSO_DPO_MSO_TDS

USE_DEVICE = 0

# Abrimos el instrumento
platforma = platform.platform()
print(platforma)
if 'pyvisa' in sys.modules:
	rm=visa.ResourceManager('@py')
	print('pyvisa')
elif 'visa' in sys.modules:
	rm=visa.ResourceManager('@ni')
	print('visa')
else:
    raise ValueError('No se pudo abrir el instrumento.')

instrument_handler=rm.open_resource(rm.list_resources()[USE_DEVICE])

if OSCILOSCOPIOS == 0:
	MiOsciloscopio = GW_Instek(instrument_handler)
elif OSCILOSCOPIOS == 1:
	MiOsciloscopio = rigol(instrument_handler)
elif OSCILOSCOPIOS == 2:
	MiOsciloscopio = Tektronix_DSO_DPO_MSO_TDS(instrument_handler)
else:
	raise ValueError('Tipo de osciloscopio fuera de lista.')


# Generamos un operador.
operador_1 = Operador_osciloscopio(MiOsciloscopio,"Workbench_I")

# Realizamos la medición.
thd = operador_1.medir_thd(canal=1,VERBOSE = True)

# Informo resultado.


