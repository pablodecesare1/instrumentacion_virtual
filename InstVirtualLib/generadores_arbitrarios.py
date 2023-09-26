# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:35:12 2018

@author: Pablo, Ramiro


Este módulo contiene las distintas implementaciones de los generadores arbitrarios.
Cada generador nuevo se debe implementar en una nueva clase que herede de la
clase base "generador_arbitrario"


"""

# Traemos la clase base que implmenta las funciones de VISA
from instrument import Instrument
# Importamos el resto de las funciones a utilizar
import numpy as np
from struct import unpack

#------------------------------------------------------------------------------
#------------------------- BASE CLASS -----------------------------------------
#------------------------------------------------------------------------------

class generador_arbitrario(Instrument):
    
    def __init__(self,handler):

        super().__init__(handler)

        self.signal=0
        self.amp=0
        self.offset=0
        self.sampleRate=0

    def dbm_Vpp(self, dbm):
        return round(10**(dbm/20)*0.775*2*np.sqrt(2),3)
    
    def clear(self, vervose=False):
        pass

    def setMemory(self):
        pass

    
#------------------------------------------------------------------------------
#------------------------- RigolDG5071 ------------------------------------------
#------------------------------------------------------------------------------


class RigolDG5071(generador_arbitrario):
    
    def __init__(self,handler):
        super().__init__(handler)
        self.signal_str=0
   
    def setArbTestMemory(self, poin_array):
        out_str = ':DATA VOLATILE,'
        for point in poin_array:
            out_str += '%0.4f, '%point
        out_str = out_str[:-2]
        self.write(out_str)
    
    def continua(self,amp=1):
        self.setArbTestMemory([1.0, 1.0])
        self.write(":APPL:USER 1,0,-%0.4f,0 "%amp)

        


#------------------------------------------------------------------------------
#------------------------- Agilent33512A ------------------------------------------
#------------------------------------------------------------------------------


class Agilent33512A(generador_arbitrario):
    
    def __init__(self,handler):
        super().__init__(handler)
        self.signal_str=0
     
    def clear(self, vervose=False):
        # Borro memoria actual
        self.write("DATA:VOLatile:CLEar")
        if vervose:
            print("memoria limpia")

    def setTestMemory(self):
        # Convierto a string
        self.numpy2string()
        # Cargo en memoria
        self.write("SOURce1:DATA:ARBitrary TestArb, {}".format(self.signal_str))

    def setArbTestMemory(self):
        self.write("SOURce1:FUNCtion:ARBitrary TestArb")

    def setScale(self, dB_scale=False):
        if dB_scale:
            use_scale = str(self.dbm_Vpp(self.amp))
        else:
            use_scale = str(self.amp)
        self.write("SOURCE1:VOLT {}".format(use_scale))

    def setOffset(self, new_offset=None):
        if new_offset != None:
            self.offset = new_offset
        self.write("SOURCE1:VOLT:OFFSET {}".format(str(self.offset)))

    def setMaxOutputImpedance(self):
        self.write("OUTPUT1:LOAD MAX")

    def setSampleRate(self):
        self.write("SOURCE1:FUNCtion:ARB:SRATe {}".format(str(self.sampleRate)))

    def setArbFunction(self, canal):
        str_out = "SOURce%d:FUNCtion ARB"%(canal+1)
        self.write(str_out)

    def encenderCanal(self, canal):
        str_out = "OUTPUT%d ON"%(canal+1)
        self.write(str_out)

    def numpy2string(self):
        lista=[]
        for puntos in self.signal:
            lista.append((puntos))
       
        self.signal_str=str(lista)
        self.signal_str=self.signal_str.replace(self.signal_str[0],"")
        self.signal_str=self.signal_str.replace(self.signal_str[-1],"")

    def set_arb_mem(self, db_scale, channel):
        # La cargo al instrumento
        self.setTestMemory()
        # Asigno un vector arbitrario
        self.setArbTestMemory()
        # Seteo la escala de tensión
        self.setScale(dB_scale=db_scale)
        # Seteo el Offset
        self.setOffset()
        # Seteo la impedancia de salida al maximo
        self.setMaxOutputImpedance()
        # Seteo el sample rate
        self.setSampleRate()
        # Seteo el modo arbitrario al canal 1
        self.setArbFunction(channel)
        # Enciendo la salida
        self.encenderCanal(channel)

        return

    def arb_signal(self,muestras, db_scale=False, amp_scale = 0, offset = 0, sample_rate=100000, channel = 0):

        self.clear()
        
        # Cargo los valores en la clase
        self.signal = muestras
        self.amp=amp_scale
        self.sampleRate = sample_rate
        self.offset=offset

        self.set_arb_mem(db_scale, channel)

        return

        


    def senoidal(self,freq=1e3,amp=0, sample_rate=100000, channel = 0):
        """ frecuencia en Hz, tension Vpp """
        
        self.clear()
        
        # Armo la señal
        memory=10000 # 1 M de memoria
        t=np.linspace(0,memory*1/sample_rate,memory)
        prueba_np=np.round(np.sin(2*np.pi*freq*t),3)

        # Cargo la señal en la clase
        self.signal = prueba_np

        self.arb_signal(prueba_np, db_scale=True, amp_scale = amp, offset = 0, sample_rate=sample_rate, channel=channel)
        
        return (t, prueba_np)
    
    def continua(self,amp=1):
        # Seteamos en DC
        self.write("SOURce1:FUNCtion DC")
        # Seteamos el valor de salida
        self.setOffset(amp)
        




#------------------------------------------------------------------------------
#------------------------- SIGLENT ------------------------------------------
#------------------------------------------------------------------------------


class Siglent1032X(generador_arbitrario):
    
    def __init__(self,handler):
        super().__init__(handler)
        self.signal_str=0
    
    def get_channel_string(self, canal):
        if canal == 0:
            return 'C1'
        elif canal == 1:
            return 'C2'
        else:
            raise ValueError('The Arb. generator has only 2 channels.')
        
    def enable_output(self, canal=0):
        self.write('{}:OUTP ON'.format(self.get_channel_string(canal)))

    def disable_output(self, canal=0):
        self.write('{}:OUTP OFF'.format(self.get_channel_string(canal)))

    def setOffset(self, new_offset=None, canal=0):
        if new_offset != None:
            self.offset = new_offset
        
        self.write("{}:BSWV OFST, {}".format(self.get_channel_string(canal), str(self.offset)))
  
    def continua(self,offset=1, canal=0):
        # Seteamos en 
        self.write('{}:BSWV WVTP, DC'.format(self.get_channel_string(canal)))
        # Seteamos el valor de salida
        self.setOffset(offset, canal=canal)

    def senoidal(self,freq=1e3,amp=0, canal = 0, offset = 0):
        """ frecuencia en Hz, tension pico """

        ch_str = self.get_channel_string(canal)

        self.write('{}:BSWV WVTP, SINE'.format(ch_str))
        self.write('{}:BSWV AMP, {}'.format(ch_str, str(amp)))
        self.write('{}:BSWV OFST, {}'.format(ch_str, str(offset)))
        self.write('{}:BSWV FRQ, {}'.format(ch_str, str(freq)))

        