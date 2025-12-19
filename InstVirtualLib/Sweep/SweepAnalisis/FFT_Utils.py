import numpy as np
from scipy.signal import windows


def _get_window(N: int, ventana: str):
    v = (ventana or "none").lower()
    if v == "hamming":
        return np.hamming(N)
    if v == "blackman":
        return np.blackman(N)
    if v in ("hanning", "hann"):
        return np.hanning(N)
    if v == "flattop":
        return windows.flattop(N, sym=False)
    if v == "none":
        return np.ones(N)
    raise ValueError(f"Ventana desconocida: {ventana}")

def fft_rfft(x, fs=1.0, ventana="none"):
    """
    rFFT one-sided + eje de frecuencias.
    Devuelve FFT cruda (sin normalizar por N).

    Returns:
      freqs: (K,)
      X: (K,) complejo
      coherent_gain: float (mean(window))
      w: (N,) ventana
    """
    x = np.asarray(x, dtype=float)
    N = x.size
    if N == 0:
        return np.array([]), np.array([], dtype=complex), 1.0, np.array([])

    w = _get_window(N, ventana)
    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(N, d=1.0 / fs)

    coherent_gain = float(np.mean(w))  # corrección de amplitud para tono
    return freqs, X, coherent_gain, w