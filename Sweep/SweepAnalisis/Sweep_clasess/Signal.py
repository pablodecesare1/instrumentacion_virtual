# =======================================================================================================
# Signal => Clase que contiene todas las mediciones que se hacen sobre el cuadripolo, asi como sus FFT's
# =======================================================================================================
import numpy as np

from Sweep.SweepAnalisis.FFT_Utils import fft_rfft
from Sweep.SweepAnalisis.Sweep_clasess.FFT_buff import FFT


class Signal:
    def __init__(self, x_in=None, x_out=None, t_in=None, t_out=None):
        self.x_in = np.asarray(x_in) if x_in is not None else np.array([])
        self.x_out = np.asarray(x_out) if x_out is not None else np.array([])
        self.t_in = np.asarray(t_in) if t_in is not None else np.array([])
        self.t_out = np.asarray(t_out) if t_out is not None else np.array([])

        self.fft_in = FFT()
        self.fft_out = FFT()

    @property
    def fs_in(self):
        if self.t_in.size < 2:
            raise ValueError("No hay suficientes muestras en t_in para calcular fs.")
        return 1.0 / (self.t_in[1] - self.t_in[0])

    @property
    def fs_out(self):
        if self.t_out.size < 2:
            raise ValueError("No hay suficientes muestras en t_out para calcular fs.")
        return 1.0 / (self.t_out[1] - self.t_out[0])

    def calculate_fft(self, ventana="none", fs_in=None, fs_out=None):
        if self.x_in.size > 0:
            fs = self.fs_in if fs_in is None else fs_in
            freqs, X, cg, _ = fft_rfft(self.x_in, fs=fs, ventana=ventana)
            self.fft_in = FFT(freqs=freqs, valores=X, N_time=self.x_in.size, coherent_gain=cg)

        if self.x_out.size > 0:
            fs = self.fs_out if fs_out is None else fs_out
            freqs, X, cg, _ = fft_rfft(self.x_out, fs=fs, ventana=ventana)
            self.fft_out = FFT(freqs=freqs, valores=X, N_time=self.x_out.size, coherent_gain=cg)

    @staticmethod
    def calculate_db(x):
        return 20 * np.log10(np.maximum(np.abs(x), 1e-300))
