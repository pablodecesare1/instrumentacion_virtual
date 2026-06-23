"""
Created on Thu May 17 09:35:12 2018

@author: Pablo, Ramiro, Juan Balbi, Joglar Matias, Niro Bruno


Este módulo contiene las distintas implementaciones de los Osciloscopios.
Cada Osciloscopio nuevo se debe implementar en una nueva clase que herede de la
clase base "Osciloscopio"


"""

# Traemos la clase base que implmenta las funciones de VISA
# Importamos el resto de las funciones a utilizar
import time as time_lib
from struct import unpack

import numpy as np

from inst_virtual_lib.instrument import Instrument

# ------------------------------------------------------------------------------
# ------------------------- BASE CLASS -----------------------------------------
# ------------------------------------------------------------------------------


class Osciloscopio(Instrument):
    def __init__(self, handler, vxi11):
        super().__init__(handler, vxi11)

    # ---- Canal Vertical
    def set_chan_div(self, valor, canal):
        pass

    def get_chan_div(self, canal):
        pass

    # ---- Canal Horizontal
    def set_bt(self, tiempo_div):
        pass

    def get_bt(self):
        pass

    def get_samplerate(self):
        pass

    # ---- Trigger
    # Setear
    def set_trigger_level(self, valor):
        pass

    def set_trigger_source(self, canal):
        raise ValueError("No implementado.")

    def set_trigger_slope(self, valor):
        pass

    def set_trigger_type(self, tipo):
        pass

    # Consultar
    def get_trigger_level(self, channel=""):
        pass

    def get_trigger_source(self):
        pass

    def get_trigger_slope(self):
        pass

    def get_trigger_type(self):
        pass

    def get_trdl(self):
        pass

    def get_trace(self, canal, verbose=1):
        pass

    def set_query_binary_values():
        pass  # hay que implementarla


# ------------------------------------------------------------------------------
# ------------------------- MSO-X 3024A Keysight ------------------------------------------
# ------------------------------------------------------------------------------


class Mso3024A(Osciloscopio):
    def __init__(self, handler):
        super().__init__(handler)

        self.SET_CH1_VDIV = "CHAN1:SCAL {}"
        self.SET_CH2_VDIV = "CHAN2:SCAL {}"
        self.SET_CH3_VDIV = "CHAN3:SCAL {}"
        self.SET_CH4_VDIV = "CHAN4:SCAL {}"

        self.GET_CH1_VDIV = "CHAN1:SCAL?"
        self.GET_CH2_VDIV = "CHAN2:SCAL?"
        self.GET_CH3_VDIV = "CHAN3:SCAL?"
        self.GET_CH4_VDIV = "CHAN4:SCAL?"

        self.read_termination = "\r"

        # ---- Canal Vertical

    def set_chan_div(self, valor, canal):
        if canal == 1:
            self.write(self.SET_CH1_VDIV.format(valor))

        if canal == 2:
            self.write(self.SET_CH2_VDIV.format(valor))

        if canal == 3:
            self.write(self.SET_CH3_VDIV.format(valor))

        if canal == 4:
            self.write(self.SET_CH4_VDIV.format(valor))

    def get_chan_div(self, canal):
        if canal == 1:
            return self.query(self.GET_CH1_VDIV)

        if canal == 2:
            return self.query(self.GET_CH2_VDIV)

        if canal == 3:
            return self.query(self.GET_CH3_VDIV)

        if canal == 4:
            return self.query(self.GET_CH4_VDIV)

    # ---- Canal Horizontal
    def set_bt(self, tiempo_div):
        self.write("TIM:SCAL " + str(tiempo_div))

    def get_bt(self):
        return self.query("TIM:SCAL?")

    # ---- Trigger
    # Setear
    def set_trigger_level(self, valor, channel):
        self.write("TRIG:LEV " + str(valor) + ", CHAN" + str(channel))

    def set_trigger_slope(self, valor):
        self.write("TRIG:SLOP " + valor)

    def set_trigger_type(self, tipo):
        self.write("TRIG:MODE " + tipo)

    # Consultar
    def get_trigger_level(self, channel):
        return self.query("TRIG:LEV? CHAN" + str(channel))

    def get_trigger_slope(self):
        return self.query("TRIG:SLOP?")

    def get_trigger_type(self):
        return self.query("TRIG:MODE?")

    def get_trace(self, canal, verbose=1):
        self.write("WAV:FORM ASCii")
        self.write("WAV:UNS OFF")
        self.write("WAV:BYT LSBF")
        self.write("WAV:SOUR CHAN" + str(canal))
        sample_rate = int(self.query("ACQ:SRAT?"))
        self.write("WAV:DATA?")

        data = self.read_raw()
        data = data[10 : len(data) - 2].decode("utf-8")
        data = np.array(data.split(","), dtype=np.float32)
        time = np.linspace(0, len(data) / sample_rate, len(data))
        return time, data

        # return(time,volt)


# ------------------------------------------------------------------------------
# ------------------------- GW_Instek ------------------------------------------
# ------------------------------------------------------------------------------


class GwInstek(Osciloscopio):
    def __init__(self, handler):
        super().__init__(handler)
        self.read_termination = "\r"

    def set_chan_div(self, valor, canal):
        if canal == 1:
            self.write(self.SET_CH1_VDIV.format(valor))
        else:
            self.write(self.SET_CH2_VDIV.format(valor))

    def get_chan_div(self, canal):
        """Retorna string del factor de division vertical del canal"""
        if canal == 1:
            return self.query(self.GET_CH1_VDIV)
        else:
            return self.query(self.GET_CH2_VDIV)

    def get_trace(self, canal, verbose=1):
        # Pedimos la escala (volt/div)
        self.write(f":CHAN{canal}:SCAL?")
        scale_1_buff = self.read_raw()
        scale = float(scale_1_buff)
        print("Escala: ", scale)

        # Pedimos el offset de la señal
        self.write(f":CHAN{canal}:OFFS?")
        offset_1_buff = self.read_raw()
        offset = float(offset_1_buff)
        print("Offset: ", offset)

        # Pedimos la escala de tiempo de la señal
        self.write(":timebase:scale?")
        time_1_buff = self.read_raw()
        time = float(time_1_buff)
        print("Base de tiempo: ", time)

        self.write(f":ACQ{canal}:MEM?")
        memoria_canal = self.read_bytes(8014, break_term=False)
        print(f"Leidos {len(memoria_canal)} datos")

        tension_volt = self.parsear_canal(memoria_canal, offset, scale, -1, verbose)
        # tiempo_seg = np.arange(0,len(tension_volt),1)*time
        tiempo_seg = np.linspace(
            0, time * 8, len(tension_volt)
        )  # 8 porque observamos eso, CHECKEAR

        return tiempo_seg, tension_volt

    def parsear_canal(self, memoria_canal, offset, scale, muestras, verbose):
        if verbose:
            print("Header en buffer:")
            print(memoria_canal[0:14])

        # Leemos el "#4", el comienzo del header de los datos
        # un char (int 8 bits) litle-endian
        h = np.frombuffer(memoria_canal, dtype=np.int8, count=1, offset=0)
        f = np.frombuffer(memoria_canal, dtype=np.int8, count=1, offset=1)

        # Leemos el resto del header, tamaño de los datos
        nn = np.frombuffer(memoria_canal, dtype=np.int8, count=4, offset=2)

        # Leemos la base de tiempo
        tb = np.frombuffer(memoria_canal, dtype=np.uint8, count=4, offset=6)
        # Viene en big-endian (IEEE 754), convertimos a little-endian
        # (revertimos el orden de los bytes)
        t = tb.newbyteorder()

        # Leemos el numero de canal del que proviene (dado antes por "ACQ#:")
        ch = np.frombuffer(memoria_canal, dtype=np.int8, count=1, offset=10)

        # Sacamos del buffer los 3 bytes reservados
        np.frombuffer(memoria_canal, dtype=np.int8, count=3, offset=11)

        if verbose:
            print("Header decodificado:")
            print(
                str(chr(h)),
                str(chr(f)),
                str(chr(nn[0])),
                str(chr(nn[1])),
                str(chr(nn[2])),
                str(chr(nn[3])),
                t,
                ch,
            )

        # Ahora convertimos los valores del ADC a volts
        #   is adc_gain the ADC mapping of 10 volts range onto 256 8-bit values
        #   ... or is it really just a magic constant of 1/25?
        adc_gain = 10.0 / 250  # todo: why not 256?  data matches for 1/25

        # Leemos 4000 cuentas crudas del ADC
        # Valores de 16 bits signados, pero el LSB es siempre 0, siendo realmente
        # valores de 8 bits
        memoria_np_canal = np.frombuffer(memoria_canal, dtype=np.int16, count=muestras, offset=14)
        memoria_np_canal = memoria_np_canal / (2**8)

        v = offset + memoria_np_canal * scale * adc_gain

        if verbose:
            print(memoria_np_canal.shape)
            print(memoria_np_canal)

        return v


# ------------------------------------------------------------------------------
# ------------------------- Tektronix_DSO_DPO_MSO_TDS --------------------------
# ------------------------------------------------------------------------------


class TektronixDsoDpoMsoTds(Instrument):
    """clase del tektronix DPO7000, MSO/DPO70000, MSO2000B / DPO2000B, MSO3000
    / DPO3000, MSO4000 / DPO4000, MSO5000 / DPO5000, TDS2000C, TDS3000, MDO3000
    , MDO4000"""

    ## comandos del vertical CH1
    SET_CH1_VDIV = "CH1:SCA {}"
    SET_CH2_VDIV = "CH1:SCA {}"
    SET_CH1_COUPLE = ""

    GET_CH1_VDIV = "CH1:SCA?"
    GET_CH2_VDIV = "CH1:SCA?"
    GET_CH1_COUPLE = ""

    ## comandos de la base de tiempo
    SET_BT = ""
    GET_BT = ""

    ## trazo

    def __init__(self, handler):
        super().__init__(handler)

    def set_chan_div(self, valor, canal):
        if canal == 1:
            self.write(self.SET_CH1_VDIV.format(valor))
        else:
            self.write(self.SET_CH2_VDIV.format(valor))

    def get_chan_div(self, canal):
        """Retorna string del factor de division vertical del canal"""
        if canal == 1:
            return self.query(self.GET_CH1_VDIV)
        else:
            return self.query(self.GET_CH2_VDIV)

    def get_trace(self, canal, verbose=1):
        """retorna una tupla (tiempo,tension)"""

        self.write(f"DATA:SOU CH{canal}")
        self.write("DATA:WIDTH 1")
        self.write("DATA:ENC RPB")

        ymult = float(self.query("WFMPRE:YMULT?"))
        yzero = float(self.query("WFMPRE:YZERO?"))
        yoff = float(self.query("WFMPRE:YOFF?"))
        xincr = float(self.query("WFMPRE:XINCR?"))
        # self.query("HORIZONTAL:RECORDLENGTH?")
        self.write("DATA:START 1")
        self.write("DATA:STOP 1000000")
        # self.query("HORIZONTAL:RECORDLENGTH?")

        self.write("CURVE?")
        data = self.read_raw()
        headerlen = 2 + int(data[1])
        adc_wave = data[headerlen:-1]

        adc_wave = np.array(unpack(f"{len(adc_wave)}B", adc_wave))

        volts = (adc_wave - yoff) * ymult + yzero
        time = np.arange(0, xincr * len(volts), xincr)
        aux = np.min((len(volts), len(time)))
        return time[0:aux], volts[0:aux]


# ------------------------------------------------------------------------------
# ------------------------- RIGOL ----------------------------------------------
# ------------------------------------------------------------------------------


class Rigol(Instrument):
    SET_CH1_VDIV = ":CHAN1:SCAL {}"
    SET_CH2_VDIV = ":CHAN2:SCAL {}"

    GET_CH1_VDIV = ":CHAN1:SCAL?"
    GET_CH2_VDIV = ":CHAN2:SCAL?"

    ## comandos de la base de tiempo
    SET_BT = ":TIM:SCAL {}"
    GET_BT = ":TIM:SCAL?"

    ## comandos de Vertical
    SET_COUPLING = ":CHANnel{0:d}:COUPling {1:}"
    GET_COUPLING = ":CHANnel{0:d}:COUPling?"

    def __init__(self, handler):
        super().__init__(handler)

    # ---- Canal Horizontal
    def set_acople(self, canal, tipo):
        self.write(self.SET_COUPLING.format(canal, tipo))

    def get_acople(self, canal):
        return self.query(self.GET_COUPLING.format(canal))

    def set_bt(self, tiempo_div):
        self.write(self.SET_BT.format(tiempo_div))

    def get_bt(self):
        return self.query(self.GET_BT)

    def set_chan_div(self, valor, canal):
        if canal == 1:
            self.write(self.SET_CH1_VDIV.format(valor))
        else:
            self.write(self.SET_CH2_VDIV.format(valor))

    def get_chan_div(self, canal):
        """Retorna string del factor de division vertical del canal"""
        if canal == 1:
            return self.query(self.GET_CH1_VDIV)
        else:
            return self.query(self.GET_CH2_VDIV)

    def get_trace(
        self,
        canal,
        sleep_time=2.0,
        adq_mode="RAW",
        adq_state="RUN",
        adq_mem_leng="LONG",
        retries=3,
        verbose=1,
    ):
        """retorna una tupla (tiempo,tension) del canal especificado"""
        canal = str(canal)

        # Estado de canala matematico
        math_state = self.query(":MATH:DISPlay?")

        # Calculamos el tamaño esperado
        # Los valores NO son los mismos del manual, fueron adaptados segun ensayo.
        if (
            adq_mode == "NORMAL" or math_state == "ON" or adq_state == "RUN"
        ):  # El manual esta mal, si esta en RUN son siempre 600
            expected_size = 600
        elif adq_mode == "RAW":
            expected_size = 16384 if adq_mem_leng == "NORM" else 1048566
        elif adq_mode == "MAX":
            if adq_mem_leng == "NORM" and adq_state == "STOP":
                expected_size = 16384
            if adq_mem_leng == "LONG" and adq_state == "STOP":
                expected_size = 1048566
            elif adq_state == "RUN":
                expected_size = 600

        # Sanity check de los parametros...
        if adq_state not in ["RUN", "STOP"]:
            print("Estado de adquisicion invalido (RUN/STOP)")
            return

        if adq_mode not in ["RAW", "MAX", "NORMAL"]:
            print("Modo de adquisicion invalido (RAW/MAX/NORMAL)")
            return

        if adq_mem_leng not in ["NORM", "LONG"]:
            print("Profundidad de memoria invalida (NORM/LONG)")
            return

        # Seteamos al modo elegido (RUN o STOP) ver manual pagina  2-69
        self.write(f":{adq_state}")
        time_lib.sleep(sleep_time)

        # Seteamos el largo de memoria
        self.write(f":ACQ:MEMD {adq_mem_leng}")
        # Modo de adquisicion
        self.write(f":WAV:POIN:MODE {adq_mode}")
        # Modo tiempo real
        self.write(":ACQ:MODE REAL_TIME")

        print(self.query(":ACQ:MEMD?"))
        print("adquisition mode: {}".format(self.query(":WAVeform:POINts:MODE?")))

        # Get the timescale
        timescale = float(self.query(":TIM:SCAL?"))
        # Get the timescale offset
        float(self.query(":TIM:OFFS?"))
        voltscale = float(self.query(f":CHAN{canal}:SCAL?"))

        # And the voltage offset
        voltoffset = float(self.query(f":CHAN{canal}:OFFS?"))

        self.write(f":WAV:DATA? CHAN{canal}")
        rawdata = self.read_raw()[10:]
        data_size = len(rawdata)

        count = 0
        while data_size != expected_size:
            count += 1
            print(
                f"Adquisition error expected {expected_size} samples"
                f" (got {data_size}), retrying ({count}/{retries})"
            )
            self.write(":RUN")
            time_lib.sleep(0.5)
            self.write(":STOP")
            time_lib.sleep(0.5)
            self.write(f":{adq_state}")

            self.write(f":WAV:DATA? CHAN{canal}")
            rawdata = self.read_raw()[10:]
            data_size = len(rawdata)

            if count >= retries:
                print("Error en la adquisicion. (numero máximo de intentos agotado)")
                return

        sample_rate = float(self.query(":ACQ:SAMP?"))
        if verbose:
            print("Data size:", data_size, "Sample rate:", sample_rate)
            print("adquisition mode: {}".format(self.query(":WAVeform:POINts:MODE?")))
            print("Math state: {}".format(self.query(":MATH:DISPlay?")))
        self.write(":KEY:FORCE")

        data = np.frombuffer(rawdata, "B")

        # Walk through the data, and map it to actual voltages
        # This mapping is from Cibo Mahto
        # First invert the data
        data = data * -1 + 255

        # Now, we know from experimentation that the scope display range is actually
        # 30-229.  So shift by 130 - the voltage offset in counts, then scale to
        # get the actual voltage.
        data = (data - 130.0 - voltoffset / voltscale * 25) / 25 * voltscale

        # Now, generate a time axis.
        if data_size != 600:
            time = np.linspace(0, len(data) / sample_rate, num=len(data))
        else:
            time = np.linspace(0, timescale * 10.0, num=len(data))

        return time, data


class SDS2102(Osciloscopio):
    def __init__(self, handler):
        super().__init__(handler)

        self.SET_CH1_VDIV = "C1:VDIV {}V"
        self.SET_CH2_VDIV = "C2:VDIV {}V"

        self.GET_CH1_VDIV = "C1:VDIV?"
        self.GET_CH2_VDIV = "C2:VDIV?"

        self.GET_SAMPLERATE = "SARA?"
        self.SET_BT = "TDIV {}S"
        self.GET_BT = "TDIV?"
        self.GET_TRDL = "TRDL?"
        self.GET_CH1_VOFFSET = "C1:OFST?"
        self.GET_CH2_VOFFSET = "C2:OFST?"

        self.SET_CH1_TRLV = "C1:TRLV {}V"
        self.SET_CH2_TRLV = "C2:TRLV {}V"

        self.read_termination = "\r"

    # ---- Vertical ----
    def set_chan_div(self, valor, canal=1):
        if canal == 1:
            self.write(self.SET_CH1_VDIV.format(valor))

        if canal == 2:
            self.write(self.SET_CH2_VDIV.format(valor))

    def set_trlv(self, valor, canal=1):
        if canal == 1:
            self.write(self.SET_CH1_TRLV.format(valor))

        if canal == 2:
            self.write(self.SET_CH1_TRLV.format(valor))

    def trace_chan(self, canal=1, encendido="ON"):
        if canal == 1:
            if encendido == "ON":
                self.write("C1:TRA ON")
            if encendido == "OFF":
                self.write("C1:TRA OFF")
        if canal == 2:
            if encendido == "ON":
                self.write("C2:TRA ON")
            if encendido == "OFF":
                self.write("C2:TRA OFF")

    def get_chan_div(self, canal=1):
        if canal == 1:
            return float(self.query(self.GET_CH1_VDIV)[8:-2])

        if canal == 2:
            return float(self.query(self.GET_CH2_VDIV)[8:-2])

    def get_voffset(self, canal=1):
        if canal == 1:
            return float(self.query(self.GET_CH1_VOFFSET)[8:-2])

        if canal == 2:
            return float(self.query(self.GET_CH1_VOFFSET)[8:-2])

    def get_samplerate(self):
        resp = self.query(self.GET_SAMPLERATE)  # Ej: "SARA 40.0KSa/s"
        parte = resp.replace("SARA", "").replace("Sa/s", "").strip()  # -> "40.0K"

        # Tomar último carácter y ver si es un sufijo conocido
        sufijo = parte[-1]
        valor = parte[:-1] + SAMPLE_RATE_DICT[sufijo] if sufijo in SAMPLE_RATE_DICT else parte

        return float(valor)

    def get_bt(self):
        bt = self.query(self.GET_BT)[4:-2]

        return float(bt)

    def set_bt(self, valor):
        return self.write(self.SET_BT.format(valor))

    def get_trdl(self):
        resp = self.query(self.GET_TRDL)
        parte = resp.replace("TRDL", "").replace("s", "").strip()

        # Tomar último carácter y ver si es un sufijo conocido
        sufijo = parte[-1]
        valor = parte[:-1] + TRIGGER_DELAY_DICT[sufijo] if sufijo in TRIGGER_DELAY_DICT else parte

        return float(valor)

    def get_template(self):
        self.write("TMPL")
        return self.read_raw()

    def wave_form_setup(self):
        self.write("WFSU SP,0,NP,0,FP,0")
        return self.read_raw()

    # ---- Obtener waveform ----
    def get_trace(self, canal=1):
        # pedir datos binarios

        if canal == 1:
            cmd = "C1:WF? DAT2"
        elif canal == 2:
            cmd = "C2:WF? DAT2"
        else:
            raise ValueError("Canal inválido, debe ser 1 o 2.")

        time_lib.sleep(0.1)  # margen por seguridad
        try:
            raw = self.instrument_handle.query_binary_values(cmd, datatype="B")
        except Exception as e:
            print("Error al leer datos binarios:", e)
            raw = np.array([])  # evita crash si falla

        # obtener parámetros escala
        vdiv = self.get_chan_div
        voffset = self.get_voffset

        sara = self.get_samplerate()
        tdiv = self.get_bt()
        trdl = self.get_trdl()

        # convertir datos a signed
        codes = np.where(raw > 127, raw - 255, raw)

        # a voltios
        volts = codes * (vdiv / 25.0) - voffset

        # eje de tiempos
        t0 = trdl - (tdiv * 14 / 2)
        dt = 1.0 / sara
        times = t0 + np.arange(len(volts)) * dt

        return times, volts


# ------------------------------------------------------------------------------
# ------------------------- RIGOL DS2202 ---------------------------------------
# ------------------------------------------------------------------------------


class RigolDs2202(Osciloscopio):
    def __init__(self, handler, vxi11):
        super().__init__(handler, vxi11)

        self.SET_CH1_VDIV = "CHAN1:SCAL {}"
        self.SET_CH2_VDIV = "CHAN2:SCAL {}"

        self.SET_CH1_OFFSET = "CHAN1:OFFS {}"
        self.SET_CH2_OFFSET = "CHAN2:OFFS {}"

        self.SET_CH1_DISPLAY = "CHAN1:DISP {}"
        self.SET_CH2_DISPLAY = "CHAN2:DISP {}"

        self.SET_TB = ":TIMebase:MAIN:SCALe {}"
        self.SET_TB_Delay = ":TIMebase:DELay:SCALe {}"
        self.SET_MEMDEPTH = ":ACQ:MDEP {}"

        self.SET_CH1_COP_DC = ":CHAN1:COUP DC"
        self.SET_CH2_COP_DC = ":CHAN2:COUP DC"

        self.SET_CH1_COP_AC = ":CHAN1:COUP AC"
        self.SET_CH2_COP_AC = ":CHAN2:COUP AC"

        self.SET_CH1_COP_GND = ":CHAN1:COUP GND"
        self.SET_CH2_COP_GND = ":CHAN2:COUP GND"

        self.set_bt_vernier = ":TIMebase:VERNier ON"
        self.unset_bt_vernier = ":TIMebase:VERNier OFF"

        self.GET_CH1_VDIV = "CHAN1:SCAL?"
        self.GET_CH2_VDIV = "CHAN2:SCAL?"

        self.GET_SAMPLE_RATE = ":ACQ:SRAT?"
        self.GET_TB = ":TIMebase:MAIN:SCALe?"
        self.GET_TB_Delay = ":TIMebase:DELay:SCALe?"
        self.GET_MEMDEPTH = ":ACQ:MDEP?"

        self.SET_TRIGGER_LVL = ":TRIGger:EDGe:LEVel {}"
        self.GET_TRIGGER_LVL = ":TRIGger:EDGe:LEVel?"

        self.SET_TRIGGER_COUP_DC = ":TRIGger:COUPling DC"
        self.SET_TRIGGER_COUP_AC = ":TRIGger:COUPling AC"
        self.GET_TRIGGER_COUP = ":TRIGger:COUPling?"

        self.SET_TRIGGER_MODE_EDGE = ":TRIGger:MODE EDGE"
        self.GET_TRIGGER_MODE = ":TRIGger:MODE?"

        self.SET_TRIGGER_EDGE_SLOPE_POS = ":TRIGger:EDGe:SLOPe POS"
        self.SET_TRIGGER_EDGE_SLOPE_NEG = ":TRIGger:EDGe:SLOPe NEG"
        self.GET_TRIGGER_EDGE_SLOPE = ":TRIGger:EDGe:SLOPe?"

        self.SET_TRIGGER_EDGE_SOURCE_CH1 = ":TRIGger:EDGe:SOURce CHAN1"

        self.SET_TRIGGER_EDGE_SOURCE_CH2 = ":TRIGger:EDGe:SOURce CHAN2"
        self.GET_TRIGGER_EDGE_SOURCE = ":TRIGger:EDGe:SOURce?"

        self.SET_CHANNEL_PROBE_CH1 = ":CHAN1:PROBe {}"
        self.SET_CHANNEL_PROBE_CH2 = ":CHAN2:PROBe {}"

        self.read_termination = "\r"

        # ---- Canal Vertical

    def set_trigger_level(self, valor):
        self.write(self.SET_TRIGGER_LVL.format(valor))

    def get_trigger_level(self):
        return self.query(self.GET_TRIGGER_LVL)

    def set_trigger_coup_ac(self):
        self.write(self.SET_TRIGGER_COUP_AC)

    def set_trigger_coup_dc(self):
        self.write(self.SET_TRIGGER_COUP_DC)

    def get_trigger_coup(self):
        return self.query(self.GET_TRIGGER_COUP)

    def set_trigger_mode_edge(self):
        self.write(self.SET_TRIGGER_MODE_EDGE)

    def get_trigger_mode(self):
        return self.query(self.GET_TRIGGER_MODE)

    def set_trigger_edge_slope_pos(self):
        self.write(self.SET_TRIGGER_EDGE_SLOPE_POS)

    def set_trigger_edge_slope_neg(self):
        self.write(self.SET_TRIGGER_EDGE_SLOPE_NEG)

    def get_trigger_edge_slope(self):
        self.query(self.GET_TRIGGER_EDGE_SLOPE)

    def set_trigger_edge_source(self, canal):
        if canal == 1:
            self.write(self.SET_TRIGGER_EDGE_SOURCE_CH1)
        if canal == 2:
            self.write(self.SET_TRIGGER_EDGE_SOURCE_CH2)

    def get_trigger_edge_source(self):
        return self.query(self.GET_TRIGGER_EDGE_SOURCE)

    def set_chan_div(self, valor, canal):  # ✅
        if canal == 1:
            self.write(self.SET_CH1_VDIV.format(valor))
        if canal == 2:
            self.write(self.SET_CH2_VDIV.format(valor))

    def set_chan_offset(self, valor, canal):  # ✅
        if canal == 1:
            self.write(self.SET_CH1_OFFSET.format(valor))
        if canal == 2:
            self.write(self.SET_CH2_OFFSET.format(valor))

    def set_chan_display(self, valor, canal):  # ✅
        if canal == 1:
            self.write(self.SET_CH1_DISPLAY.format(valor))
        if canal == 2:
            self.write(self.SET_CH2_DISPLAY.format(valor))

    def set_chan_cop_dc(self, canal):  # ✅
        if canal == 1:
            self.write(self.SET_CH1_COP_DC)
        if canal == 2:
            self.write(self.SET_CH2_COP_DC)

    def set_chan_cop_ac(self, canal):  # ✅
        if canal == 1:
            self.write(self.SET_CH1_COP_AC)
        if canal == 2:
            self.write(self.SET_CH2_COP_AC)

    def set_chan_cop_gnd(self, canal):  # ✅
        if canal == 1:
            self.write(self.SET_CH1_COP_GND)
        if canal == 2:
            self.write(self.SET_CH2_COP_GND)

    def get_chan_div(self, canal):  # ✅
        if canal == 1:
            return self.query(self.GET_CH1_VDIV)
        elif canal == 2:
            return self.query(self.GET_CH2_VDIV)

    # ---- Canal Horizontal
    def set_bt(self, valor):
        return self.write(self.SET_TB.format(valor))  # ✅

    def get_bt(self):
        return self.query(self.GET_TB)  # ✅

    def set_vernier_bt(self):
        self.write(self.set_bt_vernier)  # Sin probar

    def unset_vernier_bt(self):
        self.write(self.unset_bt_vernier)  # Sin probar

        # ---- Canal Horizontal

    def set_bt_delay(self, valor):
        return self.write(self.SET_TB_Delay.format(valor))  # Sin probar

    def get_bt_delay(self):
        return self.query(self.GET_TB_Delay)  # Sin probar

    def set_memdepth(self, valor):
        return self.write(self.SET_MEMDEPTH.format(valor))  # ✅

    def get_memdepth(self):
        return self.query(self.GET_MEMDEPTH)  # ✅

    def get_samplerate(self):
        return self.query(self.GET_SAMPLE_RATE)  # ✅

    def set_channel_prob(self, canal, valor=1):  # Sin Probar
        if canal == 1:
            self.write(self.SET_CHANNEL_PROBE_CH1.format(valor))
        if canal == 2:
            self.write(self.SET_CHANNEL_PROBE_CH2.format(valor))

    def get_trace(self, canal, verbose=1):  # ✅
        self.write(f":WAV:SOUR CHAN{canal}")
        self.write(":WAV:MODE RAW")  # leer todos los puntos
        self.write(":WAV:FORM BYTE")  # formato binario

        # --- LECTURA DEL PREÁMBULO (ESCALAS) ---
        preamble = self.query(":WAV:PRE?").split(",")
        # índices según Rigol:
        # [0]FORMAT,[1]TYPE,[2]POINTS,[3]COUNT,[4]xincr,[5]xorig,[6]XREF,[7]yincr,[8]yorig,[9]yref
        xincr = float(preamble[4])
        xorig = float(preamble[5])
        yincr = float(preamble[7])
        yorig = float(preamble[8])
        yref = float(preamble[9])

        # --- LECTURA DE DATOS BINARIOS ---
        self.write(":WAV:DATA?")
        raw = self.read_raw()

        # --- DECODIFICAR BLOQUE BINARIO #9xxxx... ---
        if raw.startswith(b"#"):
            num_digits = int(raw[1:2].decode())
            num_bytes = int(raw[2 : 2 + num_digits].decode())
            data = raw[2 + num_digits : 2 + num_digits + num_bytes]
        else:
            raise ValueError("Bloque binario inválido o encabezado no detectado")

        # --- CONVERTIR DATOS ---
        y_raw = np.frombuffer(data, dtype=np.uint8)
        y = (y_raw - yref) * yincr + yorig
        x = np.linspace(0, (len(y) - 1) * xincr, len(y)) + xorig

        return x, y


SAMPLE_RATE_DICT = {"M": "e6", "K": "e3", "G": "e9"}

TRIGGER_DELAY_DICT = {
    "u": "e-6",
    "m": "e-3",
}
