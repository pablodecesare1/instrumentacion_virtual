# -*- coding: utf-8 -*-
"""
@author: Pablo, Ramiro

Este Módulo contiene la biblioteca de mediciones. Todos los procedimientos de 
medición que se deseen automatizar se implementaran en esta clase.

La idea es que esta clase tome como entrada los vectores (tension, fase, etc)
y calcule los valores solicitados.

Todos los calculos de los 

"""

from math import floor
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import savgol_filter, windows


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
        # Calculo la fft, quedandome solo con el espectro positivo y saco la continua.
        
        yf = np.fft.fft(voltage)
        yf = yf[1:floor(len(yf)/2)]
        yf = np.abs(yf) # Obtengo el modulo

        # Calculo el indice donde esta la frecuencia fundamental
        f0_index = np.argmax(yf)
        
        # Armo vector con los indices de los armonicos
        harmonics__index = np.arange(f0_index,len(yf)-1,f0_index)
        
        # Creo vector con valores de los harmonicos
        harmonics_values = yf[harmonics__index]

        # Calculo thd
        thd = np.sqrt(np.sum(harmonics_values[1:]**2))/harmonics_values[0]
 
        return thd

    def hyst(self, x, th_lo, th_hi, initial = False):
        """
        Aplica un umbral con histeresis a un array.
        La señal de salida pasa de cero a uno cuando la
        señal de entrada supera th_hi y pasa de uno a cero
        cuando la señal de entrada pasa debajo de th_lo
        
        x: Señal
        th_lo: Umbral inferior
        th_hi: Umbral superior
        initial: Si el primer dato se encuentra dentro del umbral,
        la señal de salida comenzara valiendo "initial"
        
        Retorna: np.array
        
        Funcion original por Bas Swinckels:
        https://stackoverflow.com/a/23291658
        """
        hi = x >= th_hi
        lo_or_hi = (x <= th_lo) | hi
        ind = np.nonzero(lo_or_hi)[0]
        if not ind.size: # prevent index error if ind is empty
            return np.zeros_like(x, dtype=bool) | initial
        cnt = np.cumsum(lo_or_hi) # from 0 to len(ind)
        return np.where(cnt, hi[ind[cnt-1]], initial)


    def fft_componente_principal(self, t, v):
        """
        Encuentra la frecuencia, magnitud y fase de la
        componente principal la señal.
        
        t: Lista de puntos de tiemp
        v: Lista de puntos de tension
        
        Retorna: (frecuencia, magnitud, fase)
        
        """
        t_sample = t[1]-t[0] #Intervalo de muestreo
        
        v_windowed = v*windows.flattop(len(v)) #Utilizo una venta flat-top para mejor mediciones de amplitud

        v_fft = np.fft.fft(v_windowed)/len(v_windowed) #Calculo y normalizo FFT de la tension
        freq_fft = np.fft.fftfreq(len(v_fft), d=t_sample) #Genero lista de frecuencias correspondientes a la FFT

        #Al ser una senal real, el espectro esta espejado. Me quedo solo cun una mitad
        n_fft = round(len(v_fft)/2)  #Nuevo largo de la fft
        v_fft = v_fft[0:n_fft]
        freq_fft = freq_fft[0:n_fft]    
        
        pico_idx = np.argmax(v_fft) #Encuentro pico de magnitud
        
        #Obtengo valores
        frecuencia = freq_fft[pico_idx]
        magnitud = np.abs(v_fft[pico_idx])
        fase = np.angle(v_fft[pico_idx])
        
        return frecuencia, magnitud, fase


    def get_cruces_por_cero(self, v, direccion='ambas', delta_min=0.1):
        """
        Analiza cruces por cero de la señal. Se puede seleccionar que tipos
        de cruces se desean cambiando la variable opcional 'direccion' 
        
        v: Señal de entrada
        direccion: Posibles valores 'ambas', 'pos_a_neg', 'neg_a_pos'
        delta_min: Rango de histeresis
        
        Retorna: np.array conteniendo la lista de indices donde v cruza por cero en
        la direccion especificada
        """
        
        #Para encontrar los cruces por cero utilizo hyst() pero al introducir histeresis,
        #la señal de la salida de hyst() no corresponde al momento exacto en donde se
        #cruzo por cero. Para corregir esto, genero "vg_cruce_cero2". 
        #Esta es similar a "vg_cruce_cero1" solo que analizada en el sentido opuesto,
        #entonces los cambios de signo los detecta del lado opuesto del cruce por cero real.
        #(Asumiendo que la funcion es aproximadamente lineal en el intervalo donde actua la histeresis)
        #Promediando ambos cruces, se obtiene una mejor estimacion del cruce por cero real.

        v_cruce_cero1 = np.diff(self.hyst(v, -delta_min, delta_min).astype(int))
        v_cruce_cero2 = -np.diff(np.flip(self.hyst(np.flip(-v), -delta_min, delta_min).astype(int)))

        v_cruce_pn1 = np.where(v_cruce_cero1 < 0)[0]
        v_cruce_pn2 = np.where(v_cruce_cero2 < 0)[0]

        v_cruce_np1 = np.where(v_cruce_cero1 > 0)[0]
        v_cruce_np2 = np.where(v_cruce_cero2 > 0)[0]
        
        #Puntos en donde la señal cruza de positivo a negativo
        num_cycles = min(len(v_cruce_pn1), len(v_cruce_pn2))
        v_cruce_cero_idx_pn = np.add(v_cruce_pn1[:num_cycles], v_cruce_pn2[:num_cycles])//2 + 1    

        #Puntos en donde la señal cruza de negativo a positivo
        num_cycles = min(len(v_cruce_np1), len(v_cruce_np2))
        v_cruce_cero_idx_np = np.add(v_cruce_np1[:num_cycles], v_cruce_np2[:num_cycles])//2 + 1   
        
        if direccion == 'ambas':
            return v_cruce_cero_idx_pn + v_cruce_cero_idx_np
        
        elif direccion == 'pos_a_neg':
            return v_cruce_cero_idx_pn
        
        elif direccion == 'neg_a_pos':
            return v_cruce_cero_idx_np
        
        else:
            raise ValueError(direccion + " no es un argumento valido para \'direccion\'")


            
    def medir_RC_fft(self, t, vg, vr, R, VERBOSE=False):
        """
        Calcula la FFT de las señales de entrada para identificar la diferencia de fase de sus
        componentes principales y asi calcular la capacitancia
        """
        frec_vg, mag_vg, fase_vg = self.fft_componente_principal(t,vg)
        frec_vr, mag_vr, fase_vr = self.fft_componente_principal(t,vr)

        #Uso la informacion de la FFT para encontrar la diferencia de fase
        diff_fase = fase_vr - fase_vg


        #Calculo capacitor a partir de la diferencia de fase
        C = 1/(np.tan(diff_fase)*R*frec_vg*2*np.pi)

        if VERBOSE:
            print(f"Diferencia de fase: {diff_fase}")
            print(f"Frecuencia: {frec_vg}")

        return C

        
    def medir_RC_potencia(self, t, vg, vr, R, VERBOSE=False):
        """
        Calcula la potencia activa como el promedio de la potencia instantanea y calcula
        la potencia activa como el producto de la tension y corriente RMS. De ahi calcula
        potenica reactiva para luego calcular la reactancia del capacitor.
        """
        vg_rms = self.Vrms(t, vg)
        vr_rms = self.Vrms(t, vr)
        i_rms = vr_rms/R

        p = vr**2/R #Potencia instantanea

        P = self.Vmed(t, p) #Potenica activa
        S = vg_rms*i_rms #Potencia aparente        
        Q = np.sqrt(S**2 - P**2) #Potencia reactiva

        Xc = Q/(i_rms**2) #Reactancia capacitor
        frec_vg = self.fft_componente_principal(t,vg)[0]

        C = 1/(2*np.pi*Xc*frec_vg)
        
        if VERBOSE:
            print(f"Vg_rms: {vg_rms}")
            print(f"Vr_rms: {vr_rms}")
            print(f"i_rms: {i_rms}")
            print(f"Potencia Activa: {P}")
            print(f"Potencia Aparante: {S}")
            print(f"Potencia Reactiva: {Q}")
            print(f"Reactancia: {Xc}")
            print(f"Frecuencia: {frec_vg}")
        
        return C
        
        
    def medir_RC_lissajous(self, t, vg, vr, R, savgol=False, VERBOSE=False):
        """
        Identifica los cruces por cero de Vg y obtiene el valor de Vr para esos instantes.
        Utilizando la relacion de estos valores con los valores picos de Vr, se puede calcular
        la diferencia de fase y de ahi despejar la capacitancia.
        """
        #Elimino componente de continua
        vg = vg - self.Vmed(t, vg)
        vr = vr - self.Vmed(t, vr)

        #Calculo con la frecuencia utilizando cruces por cero
        frecuencia = 1/np.mean(np.diff(t[self.get_cruces_por_cero(vg, direccion='pos_a_neg')]))

        #Estimacion de periodo
        periodo_sampleo = t[1] - t[0]

        #Aplico filtros
        if(savgol):
            vg_filt = savgol_filter(vg, round(0.5/(periodo_sampleo*frecuencia)), 4)
            vr_filt = savgol_filter(vr,round(0.5/(periodo_sampleo*frecuencia)), 4)
        else:
            vg_filt = vg
            vr_filt = vr
        #### CALCULO A : Este es el valor pico a pico de Vr ####

        #Obotengo los picos positivos y negativos de Vr
        vg_picos_pos = self.get_cruces_por_cero(np.diff(vr_filt), direccion='pos_a_neg')
        vg_picos_neg = self.get_cruces_por_cero(np.diff(vr_filt), direccion='neg_a_pos')

        #Aseguro la misma cantidad de picos positivos y negativos
        num_ciclos = min(len(vg_picos_pos), len(vg_picos_neg)) 
        vg_picos_pos = vg_picos_pos[:num_ciclos]
        vg_picos_neg = vg_picos_neg[:num_ciclos]

        #Promedio los valores de los picos negativos, le resto el promedio de los picos negativos
        A = np.mean(vr_filt[vg_picos_pos]) - np.mean(vr_filt[vg_picos_neg]) 

        #### CALCULO B: Este es el valor al que se encuentra Vr cuando Vg cruza por cero ####

        #Obtengo los puntos donde vg cruza por cero
        vg_cruces_por_cero_pn = self.get_cruces_por_cero(vg_filt, direccion='pos_a_neg')
        vg_cruces_por_cero_np = self.get_cruces_por_cero(vg_filt, direccion='neg_a_pos')

        #Aseguro la misma cantidad de cruces positivos a negativos, y negativos a positivos
        num_ciclos = min(len(vg_cruces_por_cero_pn), len(vg_cruces_por_cero_np)) 
        vg_cruces_por_cero_pn = vg_cruces_por_cero_pn[:num_ciclos]
        vg_cruces_por_cero_np = vg_cruces_por_cero_np[:num_ciclos]

        #Promedio los valores de Vr correspondientes, restado con el promedio de los puntos opuestos
        B = np.mean(vr_filt[vg_cruces_por_cero_pn]) - np.mean(vr_filt[vg_cruces_por_cero_np]) 

        delta_fase = np.arcsin(B/A)

        C = 1/(np.tan(delta_fase)*R*frecuencia*2*np.pi)            

        if VERBOSE:
            print(f"A: {A}")
            print(f"B: {A}")
            print(f"Diferencia de fase: {delta_fase}")
            print(f"Frecuencia {frecuencia}")

        return C
        

    def medir_RC_tiempo(self, t, vg, vr, R, savgol=False, VERBOSE=False):
        """
        Encuentra los cruces por cero de Vg y Vr, calcula el retardo de la señal y luego calcula
        la diferencia de fase con la que calcula la capacitancia.
        """
        #Calculo con la frecuencia utilizando cruces por cero
        frecuencia = 1/np.mean(np.diff(t[self.get_cruces_por_cero(vg, direccion='pos_a_neg')]))

        #Estimacion de periodo
        periodo_sampleo = t[1] - t[0]

        #Aplico filtros
        if(savgol):
            vg_filt = savgol_filter(vg, round(0.5/(periodo_sampleo*frecuencia)), 4)
            vr_filt = savgol_filter(vr,round(0.5/(periodo_sampleo*frecuencia)), 4)
        else:
            vg_filt = vg
            vr_filt = vr

        tiempos_vg_pn = t[self.get_cruces_por_cero(vg_filt, direccion='pos_a_neg')]
        tiempos_vr_pn = t[self.get_cruces_por_cero(vr_filt, direccion='pos_a_neg')]

        tiempos_vg_np = t[self.get_cruces_por_cero(vg_filt, direccion='neg_a_pos')]
        tiempos_vr_np = t[self.get_cruces_por_cero(vr_filt, direccion='neg_a_pos')]

        medio_ciclo = 0.5/frecuencia


        if(tiempos_vg_pn[0] - tiempos_vr_pn[0] > medio_ciclo):
            tiempos_vr_pn = np.delete(tiempos_vr_pn, 0)

        if(tiempos_vr_pn[0] - tiempos_vg_pn[0] > medio_ciclo):
            tiempos_vg_pn = np.delete(tiempos_vg_pn, 0)

        if(tiempos_vg_pn[-1] - tiempos_vr_pn[-1] > medio_ciclo):
            tiempos_vr_pn = np.delete(tiempos_vr_pn, -1)

        if(tiempos_vr_pn[-1] - tiempos_vg_pn[-1] > medio_ciclo):
            tiempos_vg_pn = np.delete(tiempos_vg_pn, -1)

        delta_t_pn = np.mean(np.abs(tiempos_vg_pn - tiempos_vr_pn))
        delta_t_np = np.mean(np.abs(tiempos_vg_np - tiempos_vr_np))

        delta_t = (delta_t_pn + delta_t_np)/2

        delta_fase = -delta_t*frecuencia*2*np.pi

        C = 1/(2*np.pi*frecuencia*R*np.tan(delta_fase))

        if VERBOSE:
            print(f"Retardo: {delta_t}")
            print(f"Diferencia de fase: {delta_fase}")
            print(f"Frecuencia {frecuencia}")

        return C