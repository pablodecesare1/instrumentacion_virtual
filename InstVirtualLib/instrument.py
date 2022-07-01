# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:39:36 2018

@author: Pablo, Ramiro

"""

class Instrument:

    '''
    Representa tanto un instrumento de medición como de control.
    Esta clase debe contener solo la implementación de funciones VISA básicas.
    '''

    def __init__(self, visa_instrument_handle):

        # Variables o definiciones de la clase
        self.COMMAND_ID = "*IDN?"#"ID?;"
        self.COMMAND_COMM_ADDRESS = ""
        self.instrument_handle = visa_instrument_handle
        
        # Hacemos un query del ID y lo guardamos
        self.INSTR_ID = self.query(self.COMMAND_ID)
        
    def close(self):
        self.instrument_handle.before_close()
        # self.instrument_handle.clear()
        self.instrument_handle.close()

    def print_ID(self):
        print(self.INSTR_ID)


    def write(self, command_string):
        """ Implement visa write command """

        self.instrument_handle.write(command_string)

    def query(self, command_string):
        """ Implement visa query command """

        return self.instrument_handle.query(command_string)

    def read(self):
        """ Implement visa read command """
        
        return self.instrument_handle.read()

    def read_raw(self):
        """ Implement visa read raw command """
        
        return self.instrument_handle.read_raw()

    def read_bytes(self, bytes_read, break_term=True):
        """ Implement visa read bytes command """
        
        return self.instrument_handle.read_bytes(bytes_read , break_on_termchar=break_term)
