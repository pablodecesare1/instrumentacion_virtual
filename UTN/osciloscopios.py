# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:35:12 2018

@author: Pablo
"""

from instrument import Instrument
import numpy as np
from struct import unpack


class Tektronix_DSO_DPO_MSO_TDS(Instrument):
    """ clase del tektronix DPO7000, MSO/DPO70000, MSO2000B / DPO2000B, MSO3000 
    / DPO3000, MSO4000 / DPO4000, MSO5000 / DPO5000, TDS2000C, TDS3000, MDO3000
    , MDO4000 """
    
    ## comandos del vertical CH1
    SET_CH1_VDIV="CH1:SCA {}"
    SET_CH1_COUPLE=""
    GET_CH1_VDIV="CH1:SCA?"
    GET_CH1_COUPLE=""
    
    ## comandos de la base de tiempo
    SET_BT=""
    GET_BT=""
    
    ## trazo
    
    def __init__(self,handler):
        super().__init__(handler)
        
    def set_ch1_DIV(self,valor):
        self.write(self.SET_CH1_VDIV.format(valor))

    def get_ch1_DIV(self):
        """ Retorna string del factor de division vertical del canal 1"""
        return self.query(self.GET_CH1_VDIV)
        
    def get_trace(self,valor):
        """retorna una tupla (tiempo,tension) """
        
        self.write('DATA:SOU CH{}'.format(valor))
        self.write('DATA:WIDTH 1')
        self.write('DATA:ENC RPB')
        
        ymult = float(self.query('WFMPRE:YMULT?'))
        yzero = float(self.query('WFMPRE:YZERO?'))
        yoff = float(self.query('WFMPRE:YOFF?'))
        xincr = float(self.query('WFMPRE:XINCR?'))
        #self.query("HORIZONTAL:RECORDLENGTH?")
        self.write("DATA:START 1")
        self.write("DATA:STOP 1000000")
        #self.query("HORIZONTAL:RECORDLENGTH?")

        self.write('CURVE?')
        data = self.read_raw()
        headerlen = 2 + int(data[1])
        ADC_wave = data[headerlen:-1]

        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
        
        Volts = (ADC_wave - yoff) * ymult  + yzero
        Time = np.arange(0, xincr * len(Volts), xincr)
        aux=np.min((len(Volts),len(Time)))
        return Time[0:aux],Volts[0:aux]


    

class rigol(Instrument):
    SET_CH1_VDIV=":CHAN1:SCAL {}"
    SET_CH1_COUPLE="" #no implementado
    GET_CH1_VDIV=":CHAN1:SCAL?" 
    GET_CH1_COUPLE=""#no implementado
    
    ## comandos de la base de tiempo
    SET_BT=""#no implementado
    GET_BT=""#no implementado
    
    def __init__(self,handler):
        super().__init__(handler)
        
    def set_ch1_DIV(self,valor):
        self.write(self.SET_CH1_VDIV.format(valor))
    
    def get_ch1_DIV(self):
        """ Retorna string del factor de division vertical del canal 1"""
        return self.query(self.GET_CH1_VDIV)
        
    def get_trace(self,canal):
        """retorna una tupla (tiempo,tension) del canal especificado """
        canal=str(canal)
        self.write(":STOP")
 
        # Get the timescale
        timescale = float(self.query(":TIM:SCAL?"))
        # Get the timescale offset
        timeoffset = float(self.query(":TIM:OFFS?"))
        voltscale = float(self.query(':CHAN{}:SCAL?'.format(canal)))

        # And the voltage offset
        voltoffset = float(self.query(":CHAN{}:OFFS?".format(canal)))

        self.write(":WAV:POIN:MODE RAW")
        self.write(":WAV:DATA? CHAN{}".format(canal))
        rawdata = self.read_raw()[10:]
        data_size = len(rawdata)
        sample_rate = float(self.query(':ACQ:SAMP?'))
        print ('Data size:', data_size, "Sample rate:", sample_rate)
        self.write(":KEY:FORCE")
        
        data = np.frombuffer(rawdata, 'B')

        # Walk through the data, and map it to actual voltages
        # This mapping is from Cibo Mahto
        # First invert the data
        data = data * -1 + 255
 
        # Now, we know from experimentation that the scope display range is actually
# 30-229.  So shift by 130 - the voltage offset in counts, then scale to
# get the actual voltage.
        data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale

# Now, generate a time axis.
        time = np.linspace(0,len(data)/sample_rate, num=len(data))
 
        return time,data
        


class Insteck(Instrument):
    pass

class Agilent(Instrument):
    pass
