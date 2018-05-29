# -*- coding: utf-8 -*-
"""
Created on Fri May 11 19:54:23 2018

@author: Administrador
"""

import visa
import numpy as np
import matplotlib.pyplot as plt

from instruments.instruments import instruments_manager

rm = visa.ResourceManager()
print(rm.list_resources())
inst_handle = rm.open_resource(rm.list_resources()[0])
#tester = keysightN9912A.KeysightN9912A(inst_handle)
instrMgr = instruments_manager.InstrumentManager()

tester = instrMgr.search('9912')

## prueba de algunos seteos ##

tester.write(tester.COMMAND_SET_CENTER_FREQ.format("1e9")) 
tester.write(tester.COMMAND_SET_SPAN.format("1e6"))
tester.write(tester.COMMAND_SET_RBW.format("1e6"))
tester.write(tester.COMMAND_SET_VBW.format("1e6"))
tester.write(tester.COMMAND_SET_REF_LEVEL.format("20"))

tester.write(tester.COMMAND_SET_DET_SAMPLE) 

tester.write(tester.COMMAND_TAKE_SWEEP) 
tester.write(tester.COMMAND_PEAK_SEARCH)   


fcia=tester.query(tester.COMMAND_GET_MARKER_FREQ)
level=tester.query(tester.COMMAND_GET_MARKER_AMPLITUDE)
#tester.query(tester.COMMAND_GET_TRACE_DATA)
#tester.query(tester.COMMAND_GET_FREQ_DATA)
#frequ= tester.query(tester.COMMAND_GET_FREQ_DATA)
trace=np.fromstring(tester.query(tester.COMMAND_GET_TRACE_DATA), dtype=float,sep=",")
plt.plot(trace)

print(fcia,level)
