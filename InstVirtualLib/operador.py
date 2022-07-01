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
