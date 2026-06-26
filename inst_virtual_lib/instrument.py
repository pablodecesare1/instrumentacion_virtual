"""
Created on Thu May 17 09:39:36 2018

@author: Pablo, Ramiro

"""


class Instrument:
    """
    Representa tanto un instrumento de medición como de control.
    Esta clase debe contener solo la implementación de funciones VISA básicas.
    """

    def __init__(self, instrument_handle):
        # Variables o definiciones de la clase
        self.COMMAND_ID = "*IDN?"  # "ID?;"
        self.COMMAND_COMM_ADDRESS = ""

        # TODO: Checkear si el handler es de tipo X11
        # if ....
        self.connector_is_usb = True
        # else:
        # self.connector_is_usb = False
        self.instrument_handle = instrument_handle

        # Hacemos un query del ID y lo guardamos
        self.INSTR_ID = self.query(self.COMMAND_ID)

    def close(self):
        if self.connector_is_usb:
            self.instrument_handle.before_close()  # wtf??
            # self.instrument_handle.clear()

        self.instrument_handle.close()

    def print_id(self):
        idn = self.INSTR_ID
        print(idn)
        return idn

    def write(self, command_string):
        """Implement visa write command"""

        self.instrument_handle.write(command_string)

    def query(self, command_string):
        """Implement visa query command"""

        return (
            self.instrument_handle.query(command_string)
            if self.connector_is_usb
            else self.instrument_handle.ask(command_string)
        )

    def read(self):
        """Implement visa read command"""

        return self.instrument_handle.read()

    def read_raw(self):
        """Implement visa read raw command"""

        return self.instrument_handle.read_raw()

    def read_bytes(self, bytes_read, break_term=True):
        """Implement visa read bytes command"""

        return (
            self.instrument_handle.read_bytes(bytes_read, break_on_termchar=break_term)
            if self.connector_is_usb
            else self.instrument_handle.read_raw()
        )
