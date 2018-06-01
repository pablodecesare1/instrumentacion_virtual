# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:31:16 2018

@author: Pablo
"""

import visa
import matplotlib.pyplot as plt
import numpy as np
from osciloscopios import rigol
from unittest import mock



def trace_generator(canal):
    canal=str(canal)
    memory_depth=2500 #
    sample_rate=500e3 #
    BT=500e-6
    tiempo_de_captura=10*BT
    
    if canal=="1":
        fase=0        
        return (np.linspace(0,tiempo_de_captura,memory_depth),np.sin(2*np.pi*1000*np.linspace(0,tiempo_de_captura,memory_depth)+fase)+0.05*np.random.rand(memory_depth))

    elif canal=="2":
        fase=np.pi/2        
        return (np.linspace(0,tiempo_de_captura,memory_depth),np.sin(2*np.pi*1000*np.linspace(0,tiempo_de_captura,memory_depth)+fase)+0.05*np.random.rand(memory_depth))




############################################################################################################
### siempre es bueno poder chequear las funciones y lo que hacemos con ella Mock es una libreria estandar ##
### que utilizo para pasarle en handler del instrumento y simular lo que devolveria                       ## 
############################################################################################################

modo="TEST"

if modo=="TEST":
    # Desarrollar codigo sin el instrumento conectado#
    instrument_handler=mock.Mock()
    MiOsciloscopio=mock.Mock(rigol(instrument_handler))
    MiOsciloscopio.get_trace.side_effect=trace_generator  # con side effect se puede llamar a una funcion
    MiOsciloscopio.get_ch1_DIV.return_value="2 V/DIV"
    
elif modo=="MEDI":
    # se instancia el instrumento#
    rm=visa.ResourceManager()
    print(rm.list_resources())
    instrument_handler=rm.open_resource(rm.list_resources()[0])
    instrument_handler.timeout=100000
    MiOsciloscopio=rigol(instrument_handler)

##########################################################
### aca pruebo acceder a los métodos de MiOsciloscopio ###
##########################################################

MiOsciloscopio.set_ch1_DIV("2")
print("escala vertical {} V/DIV".format(MiOsciloscopio.get_ch1_DIV()))

tiempo,tension1=MiOsciloscopio.get_trace(1)
tiempo,tension2=MiOsciloscopio.get_trace(2)

plt.plot(tiempo,tension1,tiempo,tension2)


#########################################################################################################################
### es bueno separar las mediciones del istrumento...es decir yo puedo medir tension, frecuencia, diferencia de fase  ###
### y a la funcion no le tiene que importar que instrumento la hizo... por eso en el modulo Mediciones_con_DSO.py     ###
### escribo las funciones que me devolveran las medidas que tome con un osciloscopio                                  ###
#########################################################################################################################

from Mediciones_con_DSO import Vp,Vrms,Vmed    # todos los import se hacen juntos..lo puse aca solo por didactica


print("El valor pico es {} V".format(Vp(tiempo,tension1)))
print("El valor RMS es {} V".format(Vrms(tiempo,tension1)))
print("El valor medio es {} V".format(Vmed(tiempo,tension1)))





