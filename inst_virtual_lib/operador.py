"""
@author: Pablo, Ramiro

La idea es que esta clase tome un intrumento como entrada, junto con los datos
que necesita (como el canal de medición) y devuelva el valor solicitado
utilizando la clase "mediciones".

Esta clase es un nivel de abstracción mas del osciloscopio donde podemos
construir métodos de medición que utilicen varias mediciones en distintos
modos.

"""

from inst_virtual_lib import mediciones


class OperadorOsciloscopio(mediciones.Mediciones):
    def __init__(self, inst, operador):
        # nombre del equipo dado por el usuario
        self.operador = operador
        # Clase de instrumento
        self.instrument = inst

    def medir_vrms(self, canal=1, verbose=False):
        if verbose:
            print(f"metodo de medicion realizado por {self.operador}")
            print(f"con el instrumento {self.instrument.print_ID()}")

        tiempo, tension = self.instrument.get_trace(canal, verbose)

        return self.vrms(tiempo, tension)

    def medir_detaf(self, canal=1, verbose=False):
        pass

    def medir_indice_mod(self, canal=1, verbose=False):
        pass

    def get_espectro(self, canal=1, ventan="uniforme", verbose=False):
        # devolver eje en frecuencia
        pass

    def medir_thd(self, canal=1, verbose=False):
        if verbose:
            print(f"metodo de medicion realizado por {self.operador}")
            print(f"con el instrumento {self.instrument.print_ID()}")

        tiempo, tension = self.instrument.get_trace(canal, verbose)

        return self.THD(tiempo, tension)

    def medir_rc(self, r, canal_vg="1", canal_vr="2", metodo="FFT", verbose=False):
        """
        Esta funcion sirve para medir el valor de un capacitor. Para esto se
        debe armar un filtro RC pasa-altos con una resistencia conocida. A la
        entrada del filtro se debe aplicar una señal senoidal. La frecuencia
        exacta no es importante, pero debe ser lo suficientemente alta como para
        observar defasaje y atenuacion entra la señal de entrada y salida, pero
        no demasiado alta como para que la salida se encuentre muy atenuada.

        R: Resistencia que se utilizo para armar el circuito en ohms
        canal_Vg: Numero del canal conectado al generador
        canal_Vr: Numero del canal conectado a la salida del filtro (Deberia
         medir la caida de tension sbore R)
        metodo: Puede tomar los valores "FFT", "Potencia", "Lissajous",
        "Tiempo". Determina que metodo se utilizara para medir la capacitancia.
        verbose: Imprime informacion de calculos intermedios

        Retorna: Valor del capacitor en faradios
        """

        if verbose:
            print("Adquiriendo Vg")
        t, vg = self.instrument.get_trace(canal_vg, verbose)
        if verbose:
            print("Adquiriendo Vr")
        t, vr = self.instrument.get_trace(canal_vr, verbose)

        if verbose:
            print("Calculando mediante metodo " + metodo)

        if metodo == "FFT":
            c = self.medir_RC_fft(t, vg, vr, r, verbose)

        elif metodo == "Potencia":
            c = self.medir_RC_potencia(t, vg, vr, r, verbose)

        elif metodo == "Lissajous":
            c = self.medir_RC_lissajous(t, vg, vr, r, verbose)

        elif metodo == "Tiempo":
            c = self.medir_RC_tiempo(t, vg, vr, r, verbose)

        else:
            raise ValueError(metodo + " no es un argumento valido para 'metodo'")

        if verbose:
            print(f"C: {c}")

        return c


class OperadorGenerador(mediciones.Mediciones):
    def __init__(self, inst, operador):
        # nombre del equipo dado por el usuario
        self.operador = operador
        # Clase de instrumento
        self.instrument = inst

    def generar_fm(self, fc, fm, delta_f, cant_muestras, offset, sample_rate=100000):
        pass

    def generar_am(self, fc, fm, m, cant_muestras, offset, sample_rate=100000):
        pass
