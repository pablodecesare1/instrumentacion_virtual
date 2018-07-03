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


class Operador(Mediciones):
    
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


