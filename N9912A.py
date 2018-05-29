# -*- coding: utf-8 -*-
"""
Created on Fri May 11 19:37:34 2018

@author: Administrador
"""

import numpy as np
import time
## CLASE N9912A

from N9030 import AgilentN9030

class N9912A(AgilentN9030):
    COMMAND_PEAK_SEARCH = ":CALC:MARK1:FUNC:MAX"
    COMMAND_GET_TRACE_DATA = ":TRAC:DATA?"
    COMMAND_GET_FREQ_DATA = ":FREQ:DATA?"
    
    #detectores
    COMMAND_SET_DET_POSITIVE=":SENS:DET:FUNC POS"
    COMMAND_SET_DET_AVERAGE = ":SENS:DET:FUNC AVER"
    COMMAND_SET_DET_SAMPLE = ":SENS:DET:FUNC SAMP"
    COMMAND_SET_DET_NEGATIVE = ":SENS:DET:FUNC NEG"
    COMMAND_GET_DET_TYPE = ":SENS:DET:FUNC?"
    
    #pass
