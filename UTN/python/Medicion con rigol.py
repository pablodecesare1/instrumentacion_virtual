# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:31:16 2018

@author: Pablo
"""

import visa
import matplotlib.pyplot as plt

from osciloscopios import rigol



rm=visa.ResourceManager()
print(rm.list_resources())
instrument_handler=rm.open_resource(rm.list_resources()[0])
instrument_handler.timeout=100000
MiOsciloscopio=rigol(instrument_handler)

MiOsciloscopio.set_ch1_DIV("2")
print("escala vertical {} V/DIV".format(MiOsciloscopio.get_ch1_DIV()))


tiempo,tension1=MiOsciloscopio.get_trace("1")
tiempo,tension2=MiOsciloscopio.get_trace("2")
#
#
plt.plot(tiempo,tension1,tiempo,tension2)

