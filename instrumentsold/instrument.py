# -*- coding: utf-8 -*-
"""
Created on Fri May 11 19:53:43 2018

@author: Administrador
"""

import inspect


class Instrument:
    '''
    Represents each generic instrument of either control or measurement

    '''
    COMMAND_ID = "ID?;"
    COMMAND_COMM_ADDRESS = ""
    QUERY_CHAR = "?"
    TERMINATION_CHAR = ";"

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

    def statusParameters(self):

        listMethods = inspect.getmembers(self, inspect.ismethod)

        listNameAndParameters = []

        for method in listMethods:

            if 'get' in method[0]:

                listNameAndParameters.append((
                    method[0].replace('get', ''), method[1]()))

        return listNameAndParameters
