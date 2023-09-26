# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:35:12 2018

@author: Pablo, Ramiro, Juan Balbi, Joglar Matias, Niro Bruno


Este módulo contiene las distintas implementaciones de los osciloscopios.
Cada osciloscopio nuevo se debe implementar en una nueva clase que herede de la
clase base "osciloscopio"


"""

# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument
# Importamos el resto de las funciones a utilizar
import numpy as np
from struct import unpack

import time as time_lib


#------------------------------------------------------------------------------
#------------------------- BASE CLASS -----------------------------------------
#------------------------------------------------------------------------------

class osciloscopio(Instrument):
    
    def __init__(self,handler):

        # comandos del vertical CH1
        SET_CH1_VDIV=""
        SET_CH1_COUPLE=""
        GET_CH1_VDIV=""
        GET_CH1_COUPLE=""

        ## comandos de la base de tiempo
        SET_BT=""
        GET_BT=""

        ## comandos de Vertical
        SET_COUPLING=""
        GET_COUPLING=""

        super().__init__(handler)

    # ---- Canal Vertical
    def set_chan_DIV(self,valor,canal):
        pass
    def get_chan_DIV(self, canal):
        pass
    
    # ---- Canal Horizontal
    def set_BT(self,tiempo_div):
        pass
    def get_BT(self):
        pass

    # ---- Trigger
    # Setear
    def set_triggerLevel(self,valor):
        pass
    def set_triggerSource(self,canal):
        pass
    def set_triggerSlope(self,valor):
        pass
    def set_triggerType(self,tipo):
        pass
    # Consultar
    def get_triggerLevel(self,channel=''):
        pass
    def get_triggerSource(self):
        pass
    def get_triggerSlope(self):
        pass
    def get_triggerType(self):
        pass

    
        
    def get_trace(self,canal, VERBOSE = 1):
        pass


#------------------------------------------------------------------------------
#------------------------- MSO-X 3024A Keysight ------------------------------------------
#------------------------------------------------------------------------------

class MSO_3024A (osciloscopio):
    def __init__(self,handler):
        super().__init__(handler)
        
        self.SET_CH1_VDIV="CHAN1:SCAL {}"
        self.SET_CH2_VDIV="CHAN2:SCAL {}"
        self.SET_CH3_VDIV="CHAN3:SCAL {}"
        self.SET_CH4_VDIV="CHAN4:SCAL {}"
        
        self.GET_CH1_VDIV="CHAN1:SCAL?"
        self.GET_CH2_VDIV="CHAN2:SCAL?"
        self.GET_CH3_VDIV="CHAN3:SCAL?"
        self.GET_CH4_VDIV="CHAN4:SCAL?"
        
        
        self.read_termination = '\r'
        
         # ---- Canal Vertical
    def set_chan_DIV(self,valor,canal):

        if canal == 1: 
            self.write(self.SET_CH1_VDIV.format(valor))
        
        if canal == 2: 
            self.write(self.SET_CH2_VDIV.format(valor))
        
        if canal == 3: 
            self.write(self.SET_CH3_VDIV.format(valor))
        
        if canal == 4: 
            self.write(self.SET_CH4_VDIV.format(valor))
        
    def get_chan_DIV(self, canal):
        if canal == 1: 
            return self.query(self.GET_CH1_VDIV)
        
        if canal == 2: 
            return self.query(self.GET_CH2_VDIV)
        
        if canal == 3: 
            return self.query(self.GET_CH3_VDIV)
        
        if canal == 4: 
            return self.query(self.GET_CH4_VDIV)
        
    
    # ---- Canal Horizontal
    def set_BT(self,tiempo_div):
        self.write("TIM:SCAL "+str(tiempo_div))
        
    def get_BT(self):
       return self.query("TIM:SCAL?")
        
    # ---- Trigger
    # Setear
    def set_triggerLevel(self,valor,channel):
        self.write("TRIG:LEV " + str(valor)+", CHAN" + str(channel))
    
    def set_triggerSlope(self,valor):
        self.write("TRIG:SLOP "+valor)
    def set_triggerType(self,tipo):
        self.write("TRIG:MODE "+tipo)
    # Consultar
    def get_triggerLevel(self,channel):
        return self.query("TRIG:LEV? CHAN" + str(channel))
        
        
    def get_triggerSlope(self):
        return self.query("TRIG:SLOP?")
        
    def get_triggerType(self):
        return self.query("TRIG:MODE?")
        
    
        
    def get_trace(self,canal, VERBOSE = 1):
        self.write("WAV:FORM ASCii")
        self.write("WAV:UNS OFF")
        self.write("WAV:BYT LSBF")
        self.write("WAV:SOUR CHAN"+str(canal))
        sample_rate = int(self.query("ACQ:SRAT?"))
        self.write("WAV:DATA?")

        data = self.read_raw()
        data = data[10:len(data)-2].decode("utf-8")
        data = np.array(data.split(','),dtype=np.float32)
        time = np.linspace(0,len(data)/sample_rate,len(data))
        return time,data
        
        #return(time,volt)

#------------------------------------------------------------------------------
#------------------------- GW_Instek ------------------------------------------
#------------------------------------------------------------------------------


class GW_Instek(osciloscopio):
    
    def __init__(self,handler):
        super().__init__(handler)
        
        SET_CH1_VDIV="CH1:SCA {}"
        SET_CH2_VDIV="CH2:SCA {}"
        GET_CH1_VDIV="CH1:SCA?"
        GET_CH2_VDIV="CH2:SCA?"
        
        
        self.read_termination = '\r'
    

    def set_chan_DIV(self,valor,canal):
        if canal == 1: 
            self.write(self.SET_CH1_VDIV.format(valor))
        else:
            self.write(self.SET_CH2_VDIV.format(valor))
    
    def get_chan_DIV(self, canal):
        """ Retorna string del factor de division vertical del canal"""
        if canal == 1: 
            return self.query(self.GET_CH1_VDIV)
        else:
            return self.query(self.GET_CH2_VDIV)

    def get_trace(self,canal, VERBOSE = 1):
        
        
        # Pedimos la escala (volt/div)
        self.write(":CHAN%s:SCAL?"%canal) 
        scale_1_buff = self.read_raw()
        scale = float(scale_1_buff)
        print("Escala: ",scale)
        
        # Pedimos el offset de la señal
        self.write(":CHAN%s:OFFS?"%canal) 
        offset_1_buff = self.read_raw();
        offset = float(offset_1_buff)
        print("Offset: ",offset)
        
        # Pedimos la escala de tiempo de la señal
        self.write(":timebase:scale?") 
        time_1_buff = self.read_raw();
        time = float(time_1_buff)
        print("Base de tiempo: ",time)
        
        self.write(':ACQ%s:MEM?'%canal)
        memoria_canal = self.read_bytes(8014, break_term=False)
        print("Leidos %d datos"%len(memoria_canal))
        
        tension_volt = self.Parsear_canal(memoria_canal, offset, scale, -1, VERBOSE)
        #tiempo_seg = np.arange(0,len(tension_volt),1)*time
        tiempo_seg = np.linspace(0,time*16,len(tension_volt))
        
        # 8 porque observamos eso, CHECKEAR
        ## OJO, *8 genera una frecuencia del doble de la real, *16 la genera bien
            
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

    
#------------------------------------------------------------------------------
#------------------------- Tektronix_DSO_DPO_MSO_TDS --------------------------
#------------------------------------------------------------------------------

   
class Tektronix_DSO_DPO_MSO_TDS(Instrument):
    """ clase del tektronix DPO7000, MSO/DPO70000, MSO2000B / DPO2000B, MSO3000 
    / DPO3000, MSO4000 / DPO4000, MSO5000 / DPO5000, TDS2000C, TDS3000, MDO3000
    , MDO4000 """
    
    ## comandos del vertical CH1
    SET_CH1_VDIV="CH1:SCA {}"
    SET_CH2_VDIV="CH1:SCA {}"
    SET_CH1_COUPLE=""
    
    GET_CH1_VDIV="CH1:SCA?"
    GET_CH2_VDIV="CH1:SCA?"
    GET_CH1_COUPLE=""
    
    ## comandos de la base de tiempo
    SET_BT=""
    GET_BT=""
    
    ## trazo
    
    def __init__(self,handler):
        super().__init__(handler)
        
    def set_chan_DIV(self,valor,canal):
        if canal == 1: 
            self.write(self.SET_CH1_VDIV.format(valor))
        else:
            self.write(self.SET_CH2_VDIV.format(valor))
    
    def get_chan_DIV(self, canal):
        """ Retorna string del factor de division vertical del canal"""
        if canal == 1: 
            return self.query(self.GET_CH1_VDIV)
        else:
            return self.query(self.GET_CH2_VDIV)
        
    def get_trace(self,canal,VERBOSE = 1):
        """retorna una tupla (tiempo,tension) """
        
        self.write('DATA:SOU CH{}'.format(canal))
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


#------------------------------------------------------------------------------
#------------------------- RIGOL ----------------------------------------------
#------------------------------------------------------------------------------


class rigol(Instrument):
    SET_CH1_VDIV=":CHAN1:SCAL {}"
    SET_CH2_VDIV=":CHAN2:SCAL {}"

    GET_CH1_VDIV=":CHAN1:SCAL?" 
    GET_CH2_VDIV=":CHAN2:SCAL?" 

    
    ## comandos de la base de tiempo
    SET_BT=":TIM:SCAL {}"
    GET_BT=":TIM:SCAL?"

    ## comandos de Vertical
    SET_COUPLING=":CHANnel{0:d}:COUPling {1:}"
    GET_COUPLING=":CHANnel{0:d}:COUPling?"



    
    def __init__(self,handler):
        super().__init__(handler)
        
    # ---- Canal Horizontal
    def set_ACOPLE(self,canal,tipo):
        self.write(self.SET_COUPLING.format(canal,tipo))
    def get_ACOPLE(self,canal):
        return self.query(self.GET_COUPLING.format(canal))
    
    def set_BT(self,tiempo_div):
        self.write(self.SET_BT.format(tiempo_div))
    def get_BT(self):
        return self.query(self.GET_BT)

    def set_chan_DIV(self,valor,canal):
        if canal == 1: 
            self.write(self.SET_CH1_VDIV.format(valor))
        else:
            self.write(self.SET_CH2_VDIV.format(valor))
    
    def get_chan_DIV(self, canal):
        """ Retorna string del factor de division vertical del canal"""
        if canal == 1: 
            return self.query(self.GET_CH1_VDIV)
        else:
            return self.query(self.GET_CH2_VDIV)
        
    def get_trace(self,canal, sleep_time=2.0, ADQ_MODE='RAW', ADQ_STATE = 'RUN', ADQ_MEM_LENG = 'LONG', RETRIES= 3, VERBOSE = 1):
        """retorna una tupla (tiempo,tension) del canal especificado """
        canal=str(canal)
        
        # Estado de canala matematico
        MATH_STATE = self.query(':MATH:DISPlay?')
        
        # Calculamos el tamaño esperado
        # Los valores NO son los mismos del manual, fueron adaptados segun ensayo.
        if ADQ_MODE == 'NORMAL' or MATH_STATE=='ON' or ADQ_STATE=='RUN': # El manual esta mal, si esta en RUN son siempre 600
            EXPECTED_SIZE = 600
        elif ADQ_MODE == 'RAW':
            if ADQ_MEM_LENG == 'NORM':
                EXPECTED_SIZE = 16384
            else:
                EXPECTED_SIZE = 1048566
        elif ADQ_MODE == 'MAX':
            if ADQ_MEM_LENG == 'NORM' and ADQ_STATE == 'STOP':
                EXPECTED_SIZE = 16384
            if ADQ_MEM_LENG == 'LONG' and ADQ_STATE == 'STOP':
                EXPECTED_SIZE = 1048566
            elif ADQ_STATE == 'RUN':
                EXPECTED_SIZE = 600
        
        # Sanity check de los parametros...
        if not ADQ_STATE in ['RUN','STOP']:
            print('Estado de adquisicion invalido (RUN/STOP)')
            return
        
        if not ADQ_MODE in ['RAW','MAX', 'NORMAL']:
            print('Modo de adquisicion invalido (RAW/MAX/NORMAL)')
            return
        
        if not ADQ_MEM_LENG in ['NORM', 'LONG']:
            print('Profundidad de memoria invalida (NORM/LONG)')
            return
            
        # Seteamos al modo elegido (RUN o STOP) ver manual pagina  2-69
        self.write(":%s"%ADQ_STATE)
        time_lib.sleep(sleep_time)
        
        # Seteamos el largo de memoria
        self.write(":ACQ:MEMD %s"%ADQ_MEM_LENG) 
        # Modo de adquisicion
        self.write(":WAV:POIN:MODE %s"%ADQ_MODE)
        # Modo tiempo real
        self.write(":ACQ:MODE REAL_TIME") 
        
        print(self.query(":ACQ:MEMD?"))
        print('adquisition mode: %s'%self.query(':WAVeform:POINts:MODE?'))
        

        
        # Get the timescale
        timescale = float(self.query(":TIM:SCAL?"))
        # Get the timescale offset
        timeoffset = float(self.query(":TIM:OFFS?"))
        voltscale = float(self.query(':CHAN{}:SCAL?'.format(canal)))

        # And the voltage offset
        voltoffset = float(self.query(":CHAN{}:OFFS?".format(canal)))

        
                
        
        self.write(":WAV:DATA? CHAN{}".format(canal))
        rawdata = self.read_raw()[10:]
        data_size = len(rawdata)
        
        count = 0
        while (data_size != EXPECTED_SIZE):
            count += 1
            print('Adquisition error expected %d samples (got %d), retrying (%d/%d)'%(EXPECTED_SIZE, data_size, count,RETRIES))
            self.write(":RUN")
            time_lib.sleep(0.5)
            self.write(":STOP")
            time_lib.sleep(0.5)
            self.write(":%s"%ADQ_STATE)
            
            self.write(":WAV:DATA? CHAN{}".format(canal))
            rawdata = self.read_raw()[10:]
            data_size = len(rawdata)
            
            
            if count >= RETRIES:
                print('Error en la adquisicion. (numero máximo de intentos agotado)')
                return
            
            
            
        
        sample_rate = float(self.query(':ACQ:SAMP?'))
        if VERBOSE:
            print ('Data size:', data_size, "Sample rate:", sample_rate)
            print('adquisition mode: %s'%self.query(':WAVeform:POINts:MODE?'))
            print('Math state: %s'%self.query(':MATH:DISPlay?'))
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
        if data_size != 600:
            time = np.linspace(0,len(data)/sample_rate, num=len(data))
        else:
            time = np.linspace(0,timescale*10.0, num=len(data))

 
        return time,data

