import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

from Sweep.SweepAnalisis.Sweep_clasess.FFT_buff import FFT


# ==================================================
# Strategy: elegir la frecuencia de analisis
# ==================================================
class BinSelectorStrategy(ABC):
    @abstractmethod
    def select_idx(self, bloque, fft_in: FFT, fft_out: FFT):
        pass


class TargetFrequencyBinSelector(BinSelectorStrategy):
    def __init__(self):
        pass
    def select_idx(self, bloque, fft_in: FFT, fft_out: FFT):
        if bloque.frecuencia is None:
            raise ValueError("bloque.frecuencia es None (no hay frecuencia objetivo).")
        idx = int(np.argmin(np.abs(fft_in.freqs - bloque.frecuencia)))
        return idx, {
            "mode": "target_frequency",
            "freq_obj": float(bloque.frecuencia),
            "f_bin_in": float(fft_in.freqs[idx]),
            "f_bin_out": float(fft_out.freqs[idx]) if fft_out.freqs.size else None,
        }


class InputPeakBinSelector(BinSelectorStrategy):
    def __init__(self, ignore_dc=True, f_min=None, f_max=None):
        self.ignore_dc = ignore_dc
        self.f_min = f_min
        self.f_max = f_max

    def select_idx(self, bloque, fft_in: FFT, fft_out: FFT):
        vals = fft_in.valores.copy()

        if self.ignore_dc and vals.size > 0:
            vals[0] = 0

        if self.f_min is not None or self.f_max is not None:
            freqs = fft_in.freqs
            mask = np.ones_like(freqs, dtype=bool)
            if self.f_min is not None:
                mask &= freqs >= self.f_min
            if self.f_max is not None:
                mask &= freqs <= self.f_max
            if not np.any(mask):
                raise ValueError("La banda f_min/f_max deja 0 bins disponibles.")
            vals[~mask] = 0

        idx = int(np.argmax(np.abs(vals)))
        return idx, {
            "mode": "input_peak",
            "freq_obj": float(bloque.frecuencia) if bloque.frecuencia is not None else None,
            "f_bin_in": float(fft_in.freqs[idx]),
            "f_bin_out": float(fft_out.freqs[idx]) if fft_out.freqs.size else None,
        }

