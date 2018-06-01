# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 09:57:19 2018

@author: RawthiL
"""

import pyvisa as visa
import matplotlib.pyplot as plt

from osciloscopios import GW_Instek



rm=visa.ResourceManager()
instr=rm.open_resource(rm.list_resources()[0])
a = instr.query('*IDN?')
print("Esta conectado un {}".format(a))

instrument_handler=rm.open_resource(rm.list_resources()[0])
MiOsciloscopio=GW_Instek(instrument_handler)


tiempo1,tension1=MiOsciloscopio.get_trace("1")
tiempo2,tension2=MiOsciloscopio.get_trace("2")

plt.plot(tiempo1,tension1,tiempo2,tension2)

