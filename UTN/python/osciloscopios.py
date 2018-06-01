# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:35:12 2018

@author: Pablo
"""

from instrument import Instrument
import numpy as np
from struct import unpack

class osciloscopio(Instrument):
    
    ## comandos del vertical CH1
    SET_CH1_VDIV=""
    SET_CH1_COUPLE=""
    GET_CH1_VDIV=""
    GET_CH1_COUPLE=""
    
    ## comandos de la base de tiempo
    SET_BT=""
    GET_BT=""
    
    def __init__(self,handler):
        super().__init__(handler)
        
    
class GW_Instek(osciloscopio):
    
    def __init__(self,handler):
        super().__init__(handler)
        
        SET_CH1_VDIV="CH1:SCA {}"
        GET_CH1_VDIV="CH1:SCA?"
        
        
        self.read_termination = '\r'
    
    def get_trace(self,valor, VERBOSE = 1):
        

        
        
        # Pedimos la escala (volt/div)
        self.write(":CHAN%s:SCAL?"%valor) 
        scale_1_buff = self.read_raw()
        scale = float(scale_1_buff)
        print("Escala: ",scale)
        
        # Pedimos el offset de la señal
        self.write(":CHAN%s:OFFS?"%valor) 
        offset_1_buff = self.read_raw();
        offset = float(offset_1_buff)
        print("Offset: ",offset)
        
        # Pedimos la escala de tiempo de la señal
        self.write(":timebase:scale?") 
        time_1_buff = self.read_raw();
        time = float(time_1_buff)
        print("Base de tiempo: ",time)

        self.write(':ACQ%s:MEM?'%valor)
        memoria_canal = self.read_bytes(8014, break_term=True)
        print("Leidos %d datos"%len(memoria_canal))
        
        tension_volt = self.Parsear_canal(memoria_canal, offset, scale, 2000, VERBOSE)
        tiempo_seg = np.arange(0,len(tension_volt),1)*time
            
        return tiempo_seg, tension_volt
    
    def Parsear_canal(self, memoria_canal, offset, scale, muestras, VERBOSE):
        if VERBOSE:
            print('Header en buffer:')
            print(memoria_canal[0:14])
        
        # Leemos el "#4", el comienzo del header de los datos
        # un char (int 8 bits) litle-endian
        h  = np.frombuffer(memoria_canal, dtype=np.int8, count=1, offset=0)
        f  = np.frombuffer(memoria_canal, dtype=np.int8, count=1, offset=1)
    
        # Leemos el resto del header, tamaño de los datos
        nn  = np.frombuffer(memoria_canal, dtype=np.int8, count=4, offset=2)
    
        # Leemos la base de tiempo
        tb = np.frombuffer(memoria_canal, dtype=np.uint8, count=4, offset=6) 
        # Viene en big-endian (IEEE 754), convertimos a little-endian (revertimos el orden de los bytes)
        t = tb.newbyteorder()
    
        # Leemos el numero de canal del que proviene (dado antes por "ACQ#:")
        ch = np.frombuffer(memoria_canal, dtype=np.int8, count=1, offset=10)
    
        # Sacamos del buffer los 3 bytes reservados
        r = np.frombuffer(memoria_canal, dtype=np.int8, count=3, offset=11)
        
        if VERBOSE:
            print("Header decodificado:")
            print(str(chr(h)), str(chr(f)), str(chr(nn[0])), str(chr(nn[1])), str(chr(nn[2])), str(chr(nn[3])), t, ch)
    
        # Ahora convertimos los valores del ADC a volts
        #   is ADCgain the ADC mapping of 10 volts range onto 256 8-bit values
        #   ... or is it really just a magic constant of 1/25?
        ADCgain = 10.0/250;  #todo: why not 256?  data matches for 1/25
    
        # Leemos 4000 cuentas crudas del ADC
        # Valores de 16 bits signados, pero el LSB es siempre 0, siendo realmente
        # valores de 8 bits
        memoria_np_canal = np.frombuffer(memoria_canal, dtype=np.int16, count=muestras, offset=14)
        memoria_np_canal = memoria_np_canal/(2**8)
    
        v = offset + memoria_np_canal*scale*ADCgain;
    
        if VERBOSE:
            print(memoria_np_canal.shape)
            print(memoria_np_canal)
    
        return v

        

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
