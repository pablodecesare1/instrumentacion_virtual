"""
Created on Thu May 17 09:35:12 2018

@author: Pablo, Ramiro


Este módulo contiene las distintas implementaciones de los generadores arbitrarios.
Cada generador nuevo se debe implementar en una nueva clase que herede de la
clase base "generador_arbitrario"


"""

# Traemos la clase base que implmenta las funciones de VISA
# Importamos el resto de las funciones a utilizar

import numpy as np

from inst_virtual_lib.instrument import Instrument

# ------------------------------------------------------------------------------
# ------------------------- BASE CLASS -----------------------------------------
# ------------------------------------------------------------------------------


class GeneradorArbitrario(Instrument):
    def __init__(self, handler):
        super().__init__(handler)

        self.signal = 0
        self.amp = 0
        self.offset = 0
        self.sampleRate = 0

    def dbm_vpp(self, dbm):
        return round(10 ** (dbm / 20) * 0.775 * 2 * np.sqrt(2), 3)

    def clear(self, vervose=False):
        pass

    def set_memory(self):
        pass


# ------------------------------------------------------------------------------
# ------------------------- RigolDG5071 ------------------------------------------
# ------------------------------------------------------------------------------


class RigolDG5071(GeneradorArbitrario):
    def __init__(self, handler):
        super().__init__(handler)
        self.signal_str = 0

    def set_arb_test_memory(self, poin_array):
        out_str = ":DATA VOLATILE,"
        for point in poin_array:
            out_str += f"{point:0.4f}, "
        out_str = out_str[:-2]
        self.write(out_str)

    def continua(self, amp=1):
        self.set_arb_test_memory([1.0, 1.0])
        self.write(f":APPL:USER 1,0,-{amp:0.4f},0 ")


# ------------------------------------------------------------------------------
# ------------------------- Agilent33512A ------------------------------------------
# ------------------------------------------------------------------------------


class Agilent33512A(GeneradorArbitrario):
    def __init__(self, handler):
        super().__init__(handler)
        self.signal_str = 0

    def clear(self, vervose=False):
        # Borro memoria actual
        self.write("DATA:VOLatile:CLEar")
        if vervose:
            print("memoria limpia")

    def set_test_memory(self):
        # Convierto a string
        self.numpy2string()
        # Cargo en memoria
        self.write(f"SOURce1:DATA:ARBitrary TestArb, {self.signal_str}")

    def set_arb_test_memory(self):
        self.write("SOURce1:FUNCtion:ARBitrary TestArb")

    def set_scale(self, db_scale=False):
        use_scale = str(self.dbm_vpp(self.amp)) if db_scale else str(self.amp)
        self.write(f"SOURCE1:VOLT {use_scale}")

    def set_offset(self, new_offset=None):
        if new_offset is not None:
            self.offset = new_offset
        self.write(f"SOURCE1:VOLT:OFFSET {str(self.offset)}")

    def set_max_output_impedance(self):
        self.write("OUTPUT1:LOAD MAX")

    def set_sample_rate(self):
        self.write(f"SOURCE1:FUNCtion:ARB:SRATe {str(self.sampleRate)}")

    def set_arb_function(self, canal):
        str_out = f"SOURce{(canal + 1)}:FUNCtion ARB"
        self.write(str_out)

    def encender_canal(self, canal):
        str_out = f"OUTPUT{(canal + 1)} ON"
        self.write(str_out)

    def numpy2string(self):
        lista = []
        for puntos in self.signal:
            lista.append(puntos)

        self.signal_str = str(lista)
        self.signal_str = self.signal_str.replace(self.signal_str[0], "")
        self.signal_str = self.signal_str.replace(self.signal_str[-1], "")

    def set_arb_mem(self, db_scale, channel):
        # La cargo al instrumento
        self.set_test_memory()
        # Asigno un vector arbitrario
        self.set_arb_test_memory()
        # Seteo la escala de tensión
        self.set_scale(db_scale=db_scale)
        # Seteo el Offset
        self.set_offset()
        # Seteo la impedancia de salida al maximo
        self.set_max_output_impedance()
        # Seteo el sample rate
        self.set_sample_rate()
        # Seteo el modo arbitrario al canal 1
        self.set_arb_function(channel)
        # Enciendo la salida
        self.encender_canal(channel)

        return

    def arb_signal(
        self, muestras, db_scale=False, amp_scale=0, offset=0, sample_rate=100000, channel=0
    ):
        self.clear()

        # Cargo los valores en la clase
        self.signal = muestras
        self.amp = amp_scale
        self.sampleRate = sample_rate
        self.offset = offset

        self.set_arb_mem(db_scale, channel)

        return

    def senoidal(self, freq=1e3, amp=0, sample_rate=100000, channel=0):
        """frecuencia en Hz, tension Vpp"""

        self.clear()

        # Armo la señal
        memory = 10000  # 1 M de memoria
        t = np.linspace(0, memory * 1 / sample_rate, memory)
        prueba_np = np.round(np.sin(2 * np.pi * freq * t), 3)

        # Cargo la señal en la clase
        self.signal = prueba_np

        self.arb_signal(
            prueba_np,
            db_scale=True,
            amp_scale=amp,
            offset=0,
            sample_rate=sample_rate,
            channel=channel,
        )

        return (t, prueba_np)

    def continua(self, amp=1):
        # Seteamos en DC
        self.write("SOURce1:FUNCtion DC")
        # Seteamos el valor de salida
        self.set_offset(amp)


# ------------------------------------------------------------------------------
# ------------------------- SIGLENT ------------------------------------------
# ------------------------------------------------------------------------------


class Siglent1032X(GeneradorArbitrario):
    def __init__(self, handler):
        super().__init__(handler)
        self.signal_str = 0

    def get_channel_string(self, canal):
        if canal == 0:
            return "C1"
        elif canal == 1:
            return "C2"
        else:
            raise ValueError("The Arb. generator has only 2 channels.")

    def enable_output(self, canal=0):
        self.write(f"{self.get_channel_string(canal)}:OUTP ON")

    def disable_output(self, canal=0):
        self.write(f"{self.get_channel_string(canal)}:OUTP OFF")

    def set_offset(self, new_offset=None, canal=0):
        if new_offset is not None:
            self.offset = new_offset

        self.write(f"{self.get_channel_string(canal)}:BSWV OFST, {str(self.offset)}")

    def continua(self, offset=1, canal=0):
        # Seteamos en
        self.write(f"{self.get_channel_string(canal)}:BSWV WVTP, DC")
        # Seteamos el valor de salida
        self.set_offset(offset, canal=canal)

    def senoidal(self, freq=1e3, amp=0, canal=0, offset=0):
        """frecuencia en Hz, tension pico"""

        ch_str = self.get_channel_string(canal)

        self.write(f"{ch_str}:BSWV WVTP, SINE")
        self.write(f"{ch_str}:BSWV AMP, {str(amp)}")
        self.write(f"{ch_str}:BSWV OFST, {str(offset)}")
        self.write(f"{ch_str}:BSWV FRQ, {str(freq)}")
