# -*- coding: utf-8 -*-
"""
@author: Pablo, Ramiro

Este Módulo contiene la biblioteca de mediciones. Todos los procedimientos de 
medición que se deseen automatizar se implementaran en esta clase.

La idea es que esta clase tome como entrada los vectores (tension, fase, etc)
y calcule los valores solicitados.

Todos los calculos de los 

"""

import numpy as np


class Mediciones():
    
    def __init__(self):
        pass

    def Vp(self, tiempo,tension):
        """  devuelve el valor pico max """
        return np.max(tension)

    def Vrms(self, tiempo,tension):
        """ retorna el valor RMS de la señal """
        return np.sqrt(np.average(tension**2))
	    

    def Vmed(self, tiempo,tension):
        """ retorna el valor medio de modulo de la señal"""
        return np.average(tension)

    def Indice_MOD(self, tiempo,tension):
        """ retorna el indice de modulacion de una señal modulada en AM"""
        pass

    def Delta_f(self, tiempo,tension,fc):
        """ devuelve el valor de desviacion en frecuencia dada una frecuencia de portadora fc"""
        pass


        
