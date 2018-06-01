# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:31:16 2018

@author: Pablo
"""

import visa
import matplotlib.pyplot as plt

from osciloscopios import Tektronix_DSO_DPO_MSO_TDS



rm=visa.ResourceManager()
print(rm.list_resources())
instrument_handler=rm.open_resource(rm.list_resources()[0])
MiOsciloscopio=Tektronix_DSO_DPO_MSO_TDS(instrument_handler)


tiempo1,tension1=MiOsciloscopio.get_trace("1")
tiempo2,tension2=MiOsciloscopio.get_trace("2")

plt.plot(tiempo1,tension1,tiempo2,tension2)

