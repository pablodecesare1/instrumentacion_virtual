import matplotlib.pyplot as plt

import time
import vxi11
import pyvisa as visa

# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'InstVirtualLib')
# Traemos todos los osciloscopios
from InstVirtualLib.osciloscopios import RIGOL_DS2202

#cosas para que lo de juanpi funque:
import numpy as np
from numpy.fft import fft
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy import special
from scipy import stats
from scipy.signal import butter, filtfilt, firwin, sosfilt
from scipy.signal import windows
from scipy.signal import cheby1, sosfiltfilt, sosfreqz
from scipy.stats import rice
import math

from concurrent.futures import ThreadPoolExecutor, as_completed
from IPython.display import clear_output
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed

# @title PARAMETRIA
noisy_filter = False #DEFAULT: FALSE
desfasaje =  np.pi/3 #DEFAULT: 0
ruido = 3
ciclos = 15
n_muestras=100_023


# @title func act
def fft_mine_2(x, fs=1.0, ventana="none"):
    """
    Calcula la FFT de una señal y devuelve tanto la FFT como el eje de frecuencias (Hz).

    Parámetros
    ----------
    x : array-like
        Señal de entrada (una sola realización o un periodo).
    fs : float
        Frecuencia de muestreo.
    ventana : str
        Tipo de ventana ('hamming', 'blackman', 'hann', None).

    Retorna
    -------
    f : np.ndarray
        Eje de frecuencias (Hz).
    X : np.ndarray
        FFT compleja (rfft, mitad positiva).
    """
    x = np.asarray(x)
    N = len(x)

    if ventana == "hamming":
        w = np.hamming(N)
    elif ventana == "blackman":
        w = np.blackman(N)
    elif ventana == "hanning":
        w = np.hanning(N)
    elif ventana == "flattop":
        w = windows.flattop(N, sym=False)
    else:
        w = np.ones(N)

    xw = x * w
    X = np.fft.rfft(xw)
    X = X # * 2/ N
    freqs = np.fft.rfftfreq(len(x), 1/fs)

    return freqs, X

def medir_senal(
    frecuencia,
    amplitud=6,
    printear=False,
    amp_noise=1.0,
    n_muestras=50_000,
    rng=None,
    noise_default=None,
    noise_default2=None,
):
    if rng is None:
        rng = np.random.default_rng()

    # Señal original con ruido
    t, x = generar_senal(
        frecuencia=frecuencia,
        amplitud=amplitud,
        amp_noise=amp_noise,
        n_muestras=n_muestras,
        n_ciclos=10,
        rng=rng,
    )

    fs = 1.0 / (t[1] - t[0])

    x_filt, _ = cheby_lp2_filter(
        x, fs, fc=5000, order=2, plot=printear, worN=n_muestras
    )

    # Ruido adicional post-filtro
    x_filt = make_it_noisy(
        x_filt,
        amp_noise / 2,
        rng=rng,
        noise_default=noise_default2
    )

    if printear:
        plt.figure(dpi=140)
        plt.plot(t, x)
        plt.title("Señal Original")
        plt.grid(True, which="both")

        plt.figure(dpi=140)
        plt.plot(t, x_filt)
        plt.title("Señal filtrada + ruido")
        plt.grid(True, which="both")

    señal = Señal(x_in=x, x_out=x_filt, t=t)
    señal.calculate_fft(ventana="flattop")
    return señal

# @title plotteeos

def plot_f(freqs, spec_db, marker="-", linewidth=1.0, markersize=3.0, ax=None):
    """
    Grafica un espectro en dB vs frecuencia.
    """
    if ax is None:
        ax = plt.gca()

    ax.figure.set_dpi(140)
    ax.grid(True, which="both")
    ax.semilogx(freqs, spec_db, marker, linewidth=linewidth, markersize=markersize)
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Magnitud [dB]")
    ax.set_title("Espectro en dB")
    ax.set_xlim(1, np.max(freqs))
    ax.set_ylim(np.min(spec_db) - 5, np.max(spec_db) + 5)


def plot_signal(t, x, marker="-o", linewidth = 1.0, markersize=5.0, ax = None):
    if ax==None:
        ax=plt.gca()

    ax.figure.set_dpi(140)
    ax.grid(True, which="both")
    ax.plot(t, x,linewidth=linewidth)
