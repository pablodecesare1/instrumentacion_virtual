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
import numpy as np
import scipy.signal as dsp

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
    
    def mod_y_fase_comp_principal_fft(self, tiempo, tension):
        """
    
        Parameters
        ----------
        tiempo : vector de tiempo

        tension : tension de la señal

        Returns
        -------
        valor_max_fft : valor pico de potencia

        angulo_fft : valor pico de la fase
        
        frec : frecuencia dominante de la señal
        
        Brief
        ------
        Calcula el modulo y fase de la FFT de la señal que fue pasada como parametro. Devuelve el valor de modulo fase y frecuencia del valor pico mas alto
        """
        fs=1/(tiempo[1]-tiempo[0]) 

        # Rango del espectro de fourier
        fcia=np.linspace(0,fs/2,len(tiempo)//2)

        #Aplico una ventana tipo flat top para mayor presicion
        window = dsp.flattop(len(tension)) # Ventana flat top
        tension *= window

        # obtengo modulo de transformada de fourier de las señales en cuestion
        fft_r = np.fft.fft(tension)
        fft = np.abs(fft_r)
        fft = fft[0:len(fft)//2] # elimino espectro repetido
        fft /= len(fcia) # desnormalizo la fft
        
        valor_max_fft     = np.max(fft) # valor pico de la señal
        posicion_max_fft  = np.where(fft == np.max(fft))
        angulo_fft =np.angle(fft_r[posicion_max_fft])
        
        frec = fcia[posicion_max_fft[0][0]] # Frecuencia del pico (de la senoidal) 
        # Pongo el [0] para tomar el vector de posiciones de maximos y el segundo [0] para obtener la primera ocurrencia maxima
        
        return valor_max_fft, angulo_fft, frec
    
    def separar_ciclos(self,funcion_analizar):
        """
        Funcion que recibe un vector de una medicion y devuelve los periodos incios, fines de periodo y sus cruces por cero 
        """
       
        # Busco los cruces por cero, de la señal de tensón para dividir los ciclos
        cruces_list, slopes_list = self.get_zeros_signal(funcion_analizar)
        limits_ciclos = list()
        zeros_mid_list = []
        trigger_slope = slopes_list[0] # Primera pendiente
        current_limits = np.zeros(2, dtype=np.int32)
        current_limits[0] = cruces_list[0] # Primer cruce
        for cruce, slope in zip(cruces_list, slopes_list):
          # Ignoro el primero
          if current_limits[0] == cruce:
            continue
          # Si la pendiente es igual a la inicial quiere decir que arrancÃ³ de nuevo
          if (trigger_slope == slope):
            # Agrego el final del ciclo
            current_limits[1] = cruce
            limits_ciclos.append(current_limits)
            # Donde termina una empiza el siguiente...
            current_limits = np.zeros(2, dtype=np.int32)
            current_limits[0] = cruce
          # Quiere decir q es un cruce por cero a mitad de ciclo
          else:
            zeros_mid_list.append(cruce)
        #Elimino ultimo cruce por cero
        zeros_mid_list.pop()
        return np.array(zeros_mid_list),limits_ciclos
        

    def get_zeros_signal(self, signal_in, delta_min = 5):
        """
        Parameters
        ----------
        signal_in : vector de señal

        delta_min : rango de valores tomados como cruce por cero (por defecto delta_min = 5)

        Returns
        -------
        zero_cross  : posiciones de los ceros de la señal (vector)

        cross_slope : pendientes de los puntos indicados en zero_cross (vector)

        """
        zero_cross = list()
        cross_slope = list()
        i_last = 0
        for i in range(1, signal_in.shape[0]):

          if (signal_in[i-1] <= 0) and (signal_in[i] > 0):
            if (i_last == 0) or ((i-i_last)>delta_min):
              zero_cross.append(i)
              cross_slope.append(1)
              i_last = i
          if (signal_in[i-1] >= 0) and (signal_in[i] < 0):
            if (i_last == 0) or ((i-i_last)>delta_min):
              zero_cross.append(i)
              cross_slope.append(-1)
              i_last = i

        return zero_cross, cross_slope
    
    def calculo_rc_FFT(self, valor_r, tiempo, tension_gen, tension_r):    
        """
        Parameters
        ----------
        valor_r : valor de la resistencia utilizada
    
        tiempo : vector de tiempo de las señales
            
        tension_gen: vector de tensiones del generador|
    
        tension_r: vector de tensiones de la resistencia
    
        Returns
        -------
        Devuele valor del capacitor calculado por el metodo de FFT
    
        Brief
        ----
    
        Funcion que calcula el valor de un capacitor mediante la medicion del generador y la tension en una resitencia en serie. 
        El metodo utilizado es por FFT
        """    
    
        valor_max_fft_gen, angulo_fft_gen, frec_RC= self.mod_y_fase_comp_principal_fft(tiempo, tension_gen)
        valor_max_fft_r, angulo_fft_r, frec_R= self.mod_y_fase_comp_principal_fft(tiempo, tension_r)
        
        itot= valor_max_fft_r/valor_r
        zt = (valor_max_fft_gen/itot) 
        #No se multiplica las ventanas por el coef de correccion ya que se cancelan
        
        angle_total = angulo_fft_r - angulo_fft_gen 
        Xc = zt * np.sin(angle_total) 
        
        return 1/(2*np.pi*frec_RC*Xc) #valor calculado del cap
    
    def calculo_rc_potencia(self, valor_r, tiempo, tension_gen, tension_r):
        """
        Parameters
        ----------
        valor_r : valor de la resistencia utilizada

        tiempo : vector de tiempo de las señales
        
        tension_gen: vector de tensiones del generador|

        tension_r: vector de tensiones de la resistencia

        Returns
        -------
        Devuele valor del capacitor calculado por el metodo de potencia

        Brief
        -----

        Funcion que calcula el valor de un capacitor mediante la medicion del generador y la tension en una resitencia en serie. 
        El metodo utilizado es por potencia
        """   
    
        Vrms= self.Vrms(tiempo, tension_gen)
        Irms= self.Vrms(tiempo, tension_r)/valor_r
        
        pot_aparente= Vrms * Irms
        pot_activa= Irms**2 * valor_r
        pot_reactiva= np.sqrt(pot_aparente**2 - pot_activa**2)
        
        Xc= pot_reactiva/Irms**2
        
        fft_data= self.mod_y_fase_comp_principal_fft(tiempo, tension_gen)
        frec= fft_data[2]
        
        return 1/(2*np.pi*frec*Xc)
    
    def calculo_rc_lissajous(self, valor_r, tiempo, tension_gen, tension_r):

        """
        Parameters
        ----------
        valor_r : valor de la resistencia utilizada

        tiempo : vector de tiempo de las señales
        
        tension_gen: vector de tensiones del generador|

        tension_r: vector de tensiones de la resistencia

        Returns
        -------
        Devuele valor del capacitor calculado por el metodo de Lissajous

        Brief
        -----

        Funcion que calcula el valor de un capacitor mediante la medicion del generador y la tension en una resitencia en serie. 
        El metodo utilizado es por Lissajous
        """   
        ###########################################################################
        # Paso 1: Le saco el valor medio y filtro la señal
        ###########################################################################
        tension_gen = tension_gen - self.Vmed(tiempo, tension_gen)
        tension_r = tension_r - self.Vmed(tiempo, tension_r)
        tension_gen = dsp.savgol_filter(tension_gen, 59, 4) # 59 = ventana ; 4 = grado de polinomio
        tension_r = dsp.savgol_filter(tension_r, 59, 4)

         ###########################################################################
        # Paso 2: Separar en ciclos a la señal del generador
        ###########################################################################
        zeros_mid_list, limits_ciclos = self.separar_ciclos(tension_gen)
      
        ###############################################################################
        # Paso 3: Calculo la W del generador
        ###############################################################################
        ciclos = len(limits_ciclos)
        posMin = limits_ciclos[0][0]
        posMax = limits_ciclos[-1][1]
        tiempoTotal = tiempo[posMax]-tiempo[posMin]
        T0 = tiempoTotal / ciclos
        f = 1/T0
        w = 2*np.pi*f
    
        
        ###############################################################################
        # Paso 4: Calcular A y B para cada figura de lisajouse de cada ciclo
        ###############################################################################
        ciclos_vg_list = list()
        ciclos_vr_list = list()
        zeros_vg = list()
        ciclo = 0
        for lim_ciclo in limits_ciclos:
          ciclos_vg_list.append(np.copy(tension_gen[lim_ciclo[0]:lim_ciclo[1]]))
          ciclos_vr_list.append(np.copy(tension_r[lim_ciclo[0]:lim_ciclo[1]]))
          zeros_vg.append(zeros_mid_list[ciclo] - lim_ciclo[0])
          ciclo+=1
        
        A = 0
        B = 0
        for vg_this, vr_this, zero in zip(ciclos_vg_list, ciclos_vr_list, zeros_vg):
          A += np.max(vr_this) - np.min(vr_this)
          B += np.abs( vr_this[0] - vr_this[zero] )
        A /= ciclos
        B /= ciclos
 
        
        ###############################################################################
        # Paso 5: Calculo la fase
        ###############################################################################
        fase = np.abs( np.arcsin(B/A) )
       
        
        ###############################################################################
        # Paso 6: Calculo el capacitor
        ###############################################################################
        #f = atg(XC/R))
        #tg(f) = XC/R
        #tg(f) R = 1/WC
        #C = 1/( tg(f)RW )
        C = 1/(np.tan(fase) * valor_r * w)
        return C
    
    def calculo_rc_temporal(self, valor_r, tiempo, tension_gen, tension_r):
        """
        Parameters
        ----------
        valor_r : valor de la resistencia utilizada

        tiempo : vector de tiempo de las señales
        
        tension_gen: vector de tensiones del generador|

        tension_r: vector de tensiones de la resistencia

        Returns
        -------
        Devuele valor del capacitor calculado por el metodo de desfasaje

        Brief
        -----

        Funcion que calcula el valor de un capacitor mediante la medicion del generador y la tension en una resitencia en serie. 
        El metodo utilizado es por desfasaje
        """   
         ###########################################################################
        # Paso 1: Le saco el valor medio y filtro la señal
        ###########################################################################
        tension_gen = tension_gen - self.Vmed(tiempo, tension_gen)
        tension_r = tension_r - self.Vmed(tiempo, tension_r)
        tension_gen = dsp.savgol_filter(tension_gen, 59, 4) # 59 = ventana ; 4 = grado de polinomio
        tension_r = dsp.savgol_filter(tension_r, 59, 4)

        zeros_mid_list_gen, limits_ciclos_gen = self.separar_ciclos(tension_gen)
        zeros_mid_list_r, limits_ciclos_r = self.separar_ciclos(tension_r)
        
        ###############################################################################
        # Paso 3: Calculo la W del generador
        ###############################################################################
        ciclos = len(limits_ciclos_gen)
        posMin = limits_ciclos_gen[0][0]
        posMax = limits_ciclos_gen[-1][1]
        tiempoTotal = tiempo[posMax]-tiempo[posMin]
        T0 = tiempoTotal / ciclos
        f = 1/T0
        w = 2*np.pi*f
    
        delta_t = abs(tiempo[zeros_mid_list_gen[0]] - tiempo[zeros_mid_list_r[0]])# Delta t entre ceros de la senoidal
        
        alfa = delta_t * 360 / T0 ## Medido en grados
        VpicoRC = self.Vp(tiempo,tension_gen)
        VpicoR = self.Vp(tiempo,tension_r)
        z =  VpicoRC / (VpicoR/valor_r) 
        ### Reactancia capacitiva: Xc= |Z| * sen(alfa) = 1/ (2* pi *f * C)
        Xc = np.abs( z * np.sin(alfa*np.pi/180)) 

        return 1/(2* np.pi * f * Xc)

