# -*- coding: utf-8 -*-
"""
Created on Wed May 16 15:06:04 2018

@author: Pablo
"""

import visa


rm=visa.ResourceManager()
print(rm.list_resources())
instr=rm.open_resource(rm.list_resources()[0])
a = instr.query('*IDN?')
print("Esta conectado un {}".format(a))
