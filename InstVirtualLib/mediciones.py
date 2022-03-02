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

    def THD(self,time,voltage):
        """Calculo de la distorsion armonica."""
        # Calculo la fft, quedandome solo con el espectro positivo
        xf = np.fft.fftfreq(voltage.size)
        xf = xf[:round(len(xf)/2)]
        
        yf = np.fft.fft(voltage) 
        yf = yf[:round(len(yf)/2)]


        # Encuentro la frecuencia fundamental (normalizada)
        f0 = 0
        value_f0 = 0
        # xf[1:] e yf[1:0] para no tener en cuenta la continua en la busqueda.
        for f,value in zip(xf[1:],yf[1:]):
            if  abs(value)>value_f0:
                f0 = f
                value_f0 = abs(value)


        # Cargo los armonicos.
        valores_armonicos = []

        for f,value in zip(xf[1:],yf[1:]):
            if (f0 and f % f0 == 0):
                valores_armonicos.append((f,abs(value)))

        # Calculo la thd.
        aux_sum = 0
        for t in valores_armonicos[1:]:
            aux_sum+= t[1]**2
        thd = np.sqrt(aux_sum)/valores_armonicos[0][1]


        return thd
