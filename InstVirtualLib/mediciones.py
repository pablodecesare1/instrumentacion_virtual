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

    def Vp(self, tiempo, tension):
        """  devuelve el valor pico max """
        return np.max(tension)

    def Vrms(self, tiempo, tension):
        """ retorna el valor RMS de la señal """
        return np.sqrt(np.average(tension**2))

    def Vmed(self, tiempo, tension):
        """ retorna el valor medio de modulo de la señal"""
        return np.average(tension)

    def Indice_MOD(self, tiempo, tension):
        """ retorna el indice de modulacion de una señal modulada en AM"""
        pass

    def Delta_f(self, tiempo, tension, fc):
        """ devuelve el valor de desviacion en frecuencia dada una frecuencia de portadora fc"""
        pass

    def THD(self,time,voltage,fft_samples=2000):
        """Calculo de la distorsion armonica."""
        # Calculo la fft
        xf = np.fft.fftfreq(voltage.size,d=1/fft_samples)
        yf = np.fft.fft(voltage)    
        # Encuentro la frecuencia fundamental
        f0 = 0
        value_f0 = 0
        for f,value in zip(xf,yf):
            if f>0 and abs(value)>value_f0:
                f0 = f
                value_f0 = abs(value)

        valores_armonicos = []
        for f,value in zip(xf,yf):
            # Verifico que sea multiplo de la frecuencia fundamental
            if (f0 and f % f0 == 0) and f>0:
                valores_armonicos.append((f,abs(value)))

        # Calculo la thd
        aux_sum = 0
        for t in valores_armonicos[1:]:
            aux_sum+= t[1]**2
        thd = np.sqrt(aux_sum)/valores_armonicos[0][1]

        return thd
