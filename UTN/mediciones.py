# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:40:58 2018

@author: Pablo
"""

class ch1:
    
    def __init__(self,inst,operador):
        self.operador=operador
        self.instrument=inst
        
    def medir_amplitud(self):
        print("metodo de medicion realizado por {}".format(self.operador))
        print("con el instrumento {}".format(self.instrument.query("*IDN?")))
        self.instrument.set_ch1("2")
        
        print("aca tiene que ir los pasos para medir tension")
        
