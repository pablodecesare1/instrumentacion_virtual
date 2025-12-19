# =======================================================================================================
# FFT  => Clase que contiene los valores de las FFT's calculadas, asi como su eje de frecuencias
# =======================================================================================================
import numpy as np


class FFT:
    def __init__(self, freqs=None, valores=None, N_time=None, coherent_gain=1.0):
        self.freqs = np.asarray(freqs) if freqs is not None else np.array([])
        self.valores = np.asarray(valores) if valores is not None else np.array([], dtype=complex)
        self.N_time = int(N_time) if N_time is not None else None
        self.coherent_gain = float(coherent_gain) if coherent_gain is not None else 1.0

    def amp_vpk(self):
        """
        Amplitud en V pico (aprox) para espectro one-sided.
        A[k] ≈ 2|X[k]|/N, corregido por ganancia coherente.
        DC y Nyquist se corrigen a la mitad.
        """
        if self.N_time is None or self.N_time <= 0:
            raise ValueError("FFT: falta N_time para calcular amplitud.")
        cg = max(self.coherent_gain, 1e-300)

        A = (2.0 / self.N_time) * (np.abs(self.valores) / cg)

        # DC no se duplica en espectro one-sided
        if A.size > 0:
            A[0] *= 0.5

        # Nyquist tampoco se duplica si N es par (último bin de rfft)
        if (self.N_time % 2 == 0) and (A.size > 1):
            A[-1] *= 0.5

        return A

    @staticmethod
    def db(x):
        x = np.asarray(x)
        return 20 * np.log10(np.maximum(np.abs(x), 1e-300))
