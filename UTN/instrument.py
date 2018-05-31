# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:39:36 2018

@author: Pablo
"""

class Instrument:
    '''
    Represents each generic instrument of either control or measurement

    '''
    COMMAND_ID = "ID?;"
    COMMAND_COMM_ADDRESS = ""

# ============================================================================
# ============================================================================

    def __init__(self, visa_instrument_handle):

        self.instrument_handle = visa_instrument_handle

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
        """ Implement visa read command """
        
        return self.instrument_handle.read_raw()
