# -*- coding: utf-8 -*-
"""
Created on Wed May 30 09:33:50 2018

@author: Administrador
"""

import numpy as np

def Vp(tiempo,tension):
    """  devuelve el valor pico max """
    return np.max(tension)

def Vrms(tiempo,tension):
    """ retorna el valor RMS de la señal """
    return np.sqrt(np.average(tension**2))
    

def Vmed(tiempo,tension):
    """ retorna el valor medio de modulo de la señal"""
    return np.average(tension)

def Indice_MOD(tiempo,tension):
    """ retorna el indice de modulacion de una señal modulada en AM"""
    pass

def Delta_f(tiempo,tension,fc):
    """ devuelve el valor de desviacion en frecuencia dada una frecuencia de portadora fc"""
    pass

