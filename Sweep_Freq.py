# -*- coding: utf-8 -*-
"""
@author: Ariel y Pedrito
"""

# Traemos la libreria VISA
import pyvisa as visa
from IPython.core.display_functions import clear_output

from Sweep.SweepAnalisis.Sweep_classes import BloqueIO, render_status, procesar_bloque
# Agreamos el path de las librerias
import sys
sys.path.insert(0, 'InstVirtualLib')
# Traemos la clase base que implmenta las funciones de VISA
from InstVirtualLib.osciloscopios import RIGOL_DS2202
from InstVirtualLib.generadores_arbitrarios import Siglent1032X
import platform
import matplotlib.pyplot as plt
import pandas as pd
import os
# Agregamos funcionalidades
import time


print("Inicializando instrumentos Siglent...")
USE_DEVICE1 = 0
USE_DEVICE2 = 1
# Pedimos la lista de instrumentos
platforma = platform.platform()
print(platforma)
rm1=visa.ResourceManager()
rm2=visa.ResourceManager()

##Cambiar por apertura por IP de osciloscopio y Generador en un futuro
instrument_handler1=rm1.open_resource("TCPIP::10.42.0.88::5025::INSTR")
instrument_handler2=rm2.open_resource("TCPIP::::5025::INSTR")

MiOsciloscopio = RIGOL_DS2202(instrument_handler1)
MiGenerador = Siglent1032X(instrument_handler2)

# ====================== PARÁMETROS DE BARRIDO ======================
F_START = 20.0       # Hz
F_STOP  = 20000.0    # Hz
NUM_POINTS = 180      # puntos del sweep
AMPLITUDE_VPP = 5.0  # 2 Vpp = 1 V pico
#SAMPLES = 16384      # puntos de adquisición
SAVE_PATH = "./resultados_sweep"  # carpeta donde se guardan resultados



# ===================== FUNCIONES AUXILIARES ========================

##Verificar funcion, probablemente haya que modificar
from scipy.signal import windows
import numpy as np

def analyze_fft(signal, fs, f_target):
    """
    Devuelve (amplitud Vpeak, fase rad, frecuencia_bin) para una senoidal en f_target
    usando ventana Flattop (calibrada para medición de amplitud precisa).
    """
    N = len(signal)
    win = windows.flattop(N, sym=False)

    # Normalización de la ventana: garantiza que amplitud = valor real en volts pico
    win = win * (N / np.sum(win))

    # FFT de media onda real
    Y = np.fft.rfft(signal * win)
    freqs = np.fft.rfftfreq(N, d=1/fs)

    # Buscar el bin más cercano a la frecuencia de interés
    k = np.argmin(np.abs(freqs - f_target))

    # Amplitud compleja (con corrección)
    C = 2.0 * Y[k] / N  # Factor 2 por simetría, normalizado por número de puntos

    mag = np.abs(C)
    phase = np.angle(C)
    return mag, phase, freqs[k]



def run_sweep(gen, scope:RIGOL_DS2202):
    freqs = np.geomspace(F_START, F_STOP, NUM_POINTS)
    data = {"freq_Hz": [], "mag": [], "mag_dB": [], "phase_deg": []}

    os.makedirs(SAVE_PATH, exist_ok=True)
    t0 = time.time()

    # --------------- setup de las incerts ---------------
    ganancias = np.zeros_like(freqs, dtype=float)
    incerts = np.zeros_like(freqs, dtype=float)
    phases = np.zeros_like(freqs, dtype=float)
    incerts_phases = np.zeros_like(freqs, dtype=float)
    mediciones_por_freq = 3
    estados = ["pendiente"] * len(freqs)
    # --------------- setup de las incerts ---------------

    # --------------- setup del osciloscopio  ---------------
    time_base = (1 / freqs[0])
    scope.set_BT(f"{time_base:.2f}")

    scope.set_chan_DIV(AMPLITUDE_VPP, 1)
    scope.set_chan_DIV(AMPLITUDE_VPP, 2)
    # --------------- setup del osciloscopio  ---------------



    for i, f in enumerate(freqs):
        print(f"\n[{i+1}/{NUM_POINTS}] Frecuencia = {f:.1f} Hz")

        # Configurar generador
        gen.senoidal(f, AMPLITUDE_VPP)
        
        gen.enable_output()
        
        # Configurar osciloscopio
        #scope.set_timebase((1/f)*20)  # esto si se quiere un timebase dependiendo de la frecuencia
        fs = scope.get_samplerate()

        bloque = BloqueIO(nro_mediciones=mediciones_por_freq)
        bloque.frecuencia = f

        estados[i] = "midiendo"
        render_status(freqs, estados)

        for j in range(bloque.nro_mediciones):
            # Adquirir trazas
            t1, ch1 = scope.get_trace(1)
            t2, ch2 = scope.get_trace(2)

            bloque.measure(ch1, ch2, t1, fs) # Le paso solo t1 por que tiene unicamente una base temporal
            procesar_bloque(i, bloque, estados, ganancias, incerts, phases, incerts_phases)
            render_status(freqs, estados)


        # FFT con ventana flattop
        """
        A1, phi1, f_bin1 = analyze_fft(ch1, fs, f)
        A2, phi2, f_bin2 = analyze_fft(ch2, fs, f)

        # Transferencia compleja
        H = (A2 * np.exp(1j * phi2)) / (A1 * np.exp(1j * phi1))
        mag = np.abs(H)
        mag_dB = 20 * np.log10(mag)
        phase_deg = np.degrees(np.angle(H))
        
        data["freq_Hz"].append(f)
        data["mag"].append(mag)
        data["mag_dB"].append(mag_dB)
        data["phase_deg"].append(phase_deg)

        print(f"    |H| = {mag:.4f} ({mag_dB:.2f} dB)   φ = {phase_deg:.2f}°")
        """
        # time.sleep(1)
    gen.disable_output()
    clear_output(wait=True)

    data["freq_Hz"] = freqs.tolist()
    data["mag_dB"] = ganancias.tolist()
    data["phase_deg"] = phases.tolist()

    print(f"\nSweep terminado en {time.time()-t0:.1f} s")
    print("Barrido completado ✅\n")

    df = pd.DataFrame(data)
    df.to_csv(os.path.join(SAVE_PATH, "bode_data.csv"), index=False)
    print("Datos guardados en:", os.path.join(SAVE_PATH, "bode_data.csv"))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), dpi=140, sharex=True)

    # Graficar resultados
    ax1.semilogx(freqs, ganancias, label="Ganancia [dB]")
    ax1.fill_between(
        freqs,
        ganancias - incerts,
        ganancias + incerts,
        color="red",
        alpha=0.3,
        label="±σ (Rice) [dB]"
    )

    ax1.set_ylabel("Ganancia [dB]")
    ax1.grid(True, which="both")
    ax1.legend(loc="best")

    # ---- Gráfico de Fase ----
    phases_unwrapped = np.unwrap(phases)
    ax2.semilogx(freqs, phases_unwrapped, label="Fase [rad]", color="purple")
    ax2.set_xlabel("Frecuencia [Hz]")
    ax2.set_ylabel("Fase [rad]")
    ax2.grid(True, which="both")
    ax2.fill_between(
        freqs,
        phases_unwrapped - incerts_phases,
        phases_unwrapped + incerts_phases,
        color="red",
        alpha=0.3,
        label="±σ fase"
    )
    ax2.legend(loc="best")
    ax2.set_xlim(freqs[0], freqs[-1])

    plt.tight_layout()
    plt.show()

    print(incerts_phases)

    return df

if __name__ == "__main__": 
    print("Comenzando barrido de frecuencia...\n")
    df = run_sweep(MiGenerador, MiOsciloscopio)
    print("\nAnálisis finalizado correctamente.")
