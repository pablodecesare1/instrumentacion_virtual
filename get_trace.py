# -*- coding: utf-8 -*-
"""
Created on Mon May 14 14:15:13 2018

@author: Quique
"""

import visa
import numpy as np
import pandas as pd
from io import StringIO

#Abrir instancia de VISA y analizador de espectro
rm=visa.ResourceManager()
rm.list_resources()
instr=rm.open_resource('USB0::0x2A8D::0x5C18::MY56071255::INSTR')

#capturo trazo y lo guardo en analizador
instr.write('MMEM:STOR:FDAT "MyFile.csv"')
#leer trazo (ASCII) de analizador en variable
a=instr.query('MMEM:DATA? "MyFile.csv"')

#guardo en PC el trazo con header
archivo = open("c:\\medicion.csv",mode="w")
archivo.write(a)
archivo.close()

#Me quedo sólo con la parte de los datos
""" PARA MEJORAR: buscar con expresión regular el primer
    número después de BEGIN para recortar el string.
"""
b=(a[a.find("BEGIN")+7:a.find("END")])

#Lo guardo en un pandas y lo grafico
falsoCSV = StringIO(b)
panda = pd.read_csv(falsoCSV,sep=',',header=None)
panda.plot.line(0,1)

#Ahora capturo la imagen y la guardo (BINARIO) en variable
instr.write('MMEM:STOR:IMAG "MyFile.png"; *WAI')
foto = instr.query_binary_values(':MMEM:DATA? "MyFile.png";*WAI',datatype='s')

#Finalmente la vuelco a archivo en PC
archivo = open("c:\\foto002.png",mode="wb")
archivo.write(foto[0])
archivo.close()

