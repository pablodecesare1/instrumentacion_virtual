"""
Created on Fri Oct 26 10:07:15 2018

@author: Federico Bua, Lucas Manfredi

"""

import numpy as np

from inst_virtual_lib.instrument import Instrument

# ------------------------------------------------------------------------------
# ------------------------- BASE CLASS -----------------------------------------
# ------------------------------------------------------------------------------


class AnalizadorEspectro(Instrument):
    def __init__(self, handler):
        super().__init__(handler)

    def set_freq_center(self, hz):
        pass

    def set_freq_start(self, hz):
        pass

    def set_freq_stop(self, hz):
        pass

    def set_span(self, hz):
        pass

    def set_referencelevel(self, dbm):
        pass

    def set_atenuator(self, db):
        pass

    def set_rbw(self, hz):
        pass

    def set_vbw(self, hz):
        pass

    def set_sweeptime(self, s):
        pass

    def get_marker(self):  # retornar frecuencia y amplitud
        pass

    def peaksearch(self):
        pass

    def set_marker_delta(self, marker):
        pass

    def set_marker_freq(self, marker, hz):
        pass

    def get_trace(self):
        pass


# -----------------------------------------------------------------------------
# --------------------Analizador de espectro DSA815----------------------------
# -----------------------------------------------------------------------------
class RigolDsa800(AnalizadorEspectro):
    def __init__(self, handler):
        super().__init__(handler)

    def set_freq_center(self, hz):
        self.write(":SENSe:FREQuency:CENTer " + str(hz))

    def set_freq_start(self, hz):
        self.write(":SENSe:FREQuency:STARt " + str(hz))

    def set_freq_stop(self, hz):
        self.write(":SENSe:FREQuency:STOP " + str(hz))

    def set_span(self, hz):
        self.write(":SENSe:FREQuency:SPAN " + str(hz))

    def set_referencelevel(self, dbm):
        self.write(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel " + str(dbm))

    def set_atenuator(self, db):
        self.write(":SENSe:POWer:RF:ATTenuation " + str(db))

    def set_rbw(self, hz):
        self.write(":SENSe:BANDwidth:RESolution " + str(hz))

    def set_vbw(self, hz):
        self.write(":SENSe:BANDwidth:VIDeo " + str(hz))

    def set_sweeptime(self, s):
        self.write(":SENSe:SWEep:TIME " + str(s))

    def get_marker(self, marker):
        a = self.query("CALCulate:MARKer" + str(marker) + ":Y?")
        b = self.query("CALCulate:MARKer" + str(marker) + ":X?")
        return a, b

    def peaksearch(self, marker):
        self.write(":CALCulate:MARKer" + str(marker) + ":STATe ON")  # MARKer1 2,3 o 4
        self.write(":CALCulate:MARKer" + str(marker) + "MAXImum:MAX")

    def set_marker_freq(self, marker, hz):
        self.write(":CALCulate:MARKer" + str(marker) + ":STATe ON")  # MARKer1 2,3 o 4
        self.write(":CALCulate:MARKer" + str(marker) + ":X " + str(hz))

    def get_trace(self):
        a = self.query(":TRACe:DATA? TRACE1")
        a = a[11:-1]  # Recorto el #9000009014 delantero y el \n del final
        a = np.array(
            a.split(", "), dtype=np.float32
        )  # Lo separo de las comas y lo preparo para graficar
        return a

    def set_marker_delta(self, marker):
        self.write(":CALCulate:MARKer" + str(marker) + ":STATe ON")  # MARKer1 2,3 o 4
        self.write(
            ":CALCulate:MARKer" + str(marker) + ":MODE DELT"
        )  # Mode: POS, DELT, BAND or SPAN
        # self.write(":CALCulate:MARKer"+str(marker)+":DELTa:SET:CENTer")

    def set_marker_reference_level(self, marker):
        self.write(":CALCulate:MARKer" + str(marker) + ":STATe ON")  # MARKer1 2,3 o 4
        self.write(":CALCulate:MARKer" + str(marker) + ":SET:RLEVel")
