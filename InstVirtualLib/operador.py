# -*- coding: utf-8 -*-
"""
@author: Pablo, Ramiro

La idea es que esta clase tome un intrumento como entrada, junto con los datos
que necesita (como el canal de medición) y devuelva el valor solicitado 
utilizando la clase "mediciones".

Esta clase es un nivel de abstracción mas del osciloscopio donde podemos 
construir métodos de medición que utilicen varias mediciones en distintos
modos.

"""

import numpy as np
import mediciones


class Operador_osciloscopio(mediciones.Mediciones):
    
    def __init__(self,inst,operador):
        # nombre del equipo dado por el usuario
        self.operador	= operador
        # Clase de instrumento
        self.instrument	= inst


    def medir_Vrms(self, canal = 1, VERBOSE = False):

        if VERBOSE:
            print("metodo de medicion realizado por {}".format(self.operador))
            print("con el instrumento {}".format(self.instrument.print_ID()))

        tiempo,tension = self.instrument.get_trace(canal, VERBOSE)

        return self.Vrms(tiempo,tension)
    
    def medir_detaF(self, canal = 1, VERBOSE = False):
        pass

    def medir_indiceMod(self, canal = 1, VERBOSE = False):
        pass

    def get_espectro(self, canal = 1, ventan='uniforme', VERBOSE = False):
        # devolver eje en frecuencia
        pass

    def medir_thd(self,canal=1,VERBOSE= False):
        if VERBOSE:
            print("metodo de medicion realizado por {}".format(self.operador))
            print("con el instrumento {}".format(self.instrument.print_ID()))

        tiempo,tension = self.instrument.get_trace(canal, VERBOSE)

        return self.THD(tiempo,tension)


    def medir_RC(self, R, canal_Vg = "1", canal_Vr = "2", metodo="FFT", VERBOSE = False):
        """
        Esta funcion sirve para medir el valor de un capacitor. Para esto se debe armar
        un filtro RC pasa-altos con una resistencia conocida. A la entrada del filtro se
        debe aplicar una señal senoida. La frecuencia exacta no es importante, pero debe
        ser lo suficientemente alta como para observar defasaje y atenuacion entra la señal
        de entrada y salida, pero no demasiado alta como para que la salida se encuentre muy
        atenuada.
        Para mediciones con los metodos de "Lissajous" y "Tiempo" es importante que el osciloscopio
        se encuentre trigereando la señal correctamente.


        R: Resistencia que se utilizo para armar el circuito en ohms
        canal_Vg: Numero del canal conectado al generador
        canal_Vr: Numero del canal conectado a la salida del filtro (Deberia medir la caida de tension
        sbore R)
        metodo: Puede tomar los valores "FFT", "Potencia", "Lissajous", "Tiempo". Determina que metodo se
        utilizara para medir la capacitancia.
        VERBOSE: Imprime informacion de calculos intermedios

        Retorna: Valor del capacitor en faradios
        """


        if VERBOSE:
            print("Adquiriendo Vg")
        t,vg = self.instrument.get_trace(canal_Vg, VERBOSE)
        if VERBOSE:
            print("Adquiriendo Vr")
        t,vr = self.instrument.get_trace(canal_Vr, VERBOSE)

        if VERBOSE:
            print("Calculando mediante metodo " + metodo)

        C = 0

        if metodo == "FFT":
            C = self.medir_RC_fft(t, vg, vr, R, VERBOSE)

        elif metodo == "Potencia":
            C = self.medir_RC_potencia(t, vg, vr, R, VERBOSE)

        elif metodo == "Lissajous":
            C = self.medir_RC_lissajous(t, vg, vr, R, VERBOSE)

        elif metodo == "Tiempo":
            C = self.medir_RC_tiempo(t, vg, vr, R, VERBOSE)

        else:
            raise ValueError(metodo + " no es un argumento valido para \'metodo\'")

        if VERBOSE:
            print(f"C: {C}")

        return C

class Operador_generador(mediciones.Mediciones):
    
    def __init__(self,inst,operador):
        # nombre del equipo dado por el usuario
        self.operador	= operador
        # Clase de instrumento
        self.instrument	= inst

    def generar_FM(self, fc, fm, deltaF, cant_muestras, offset, sample_rate=100000):
        pass

    def generar_AM(self, fc, fm, M, cant_muestras, offset, sample_rate=100000):
        pass
