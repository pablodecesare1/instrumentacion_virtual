# -*- coding: utf-8 -*-
"""
Barrido en frecuencia con Rigol DS2202 + Siglent 1032X.

@author: Ariel y Pedrito
"""

import os
import sys
import time
import platform

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyvisa as visa
from IPython.core.display_functions import clear_output
from numpy.random._examples.cffi.extending import rng

from Sweep.SweepAnalisis.Sweep_clasess.BloqueIO import BloqueIO
from Sweep.SweepAnalisis.Sweep_strategies import InputPeakBinSelector
from Sweep.SweepAnalisis.Sweep_utils import procesar_bloque
from Sweep.TEST.Utils_tb import CsvSignalSource

sys.path.insert(0, "InstVirtualLib")


# ====================== PARÁMETROS DE BARRIDO =========================================================================================
# ======================================================================================================================================
F_START = 20.0          # Hz
F_STOP = 20_000.0       # Hz
NUM_POINTS = 5          # cantidad de puntos del sweep
AMPLITUDE_VPP = 5.0     # Vpp
SAVE_PATH = "../resultados_sweep"  # carpeta donde se guardan resultados
MEDICIONES_POR_FREQ = 3
# ======================================================================================================================================
# ====================== PARÁMETROS DE BARRIDO =========================================================================================


# ===================== FUNCIONES AUXILIARES ========================

def run_sweep():
    print("Inicializando barrido...")
    print("Plataforma:", platform.platform())

    t0 = time.time()

    os.makedirs(SAVE_PATH, exist_ok=True)

    base_dir = "C:/TP-MEDIDAS-FINAL/instrumentacion_virtual (5)/instrumentacion_virtual/Sweep/TEST/mediciones/1kptos/"
    peak_strategy = InputPeakBinSelector(ignore_dc=True)

    src = CsvSignalSource(base_dir)
    freqs_all = src.get_frequencies()
    # si querés usar todas las frecuencias del CSV:
    freq_indices = list(range(len(freqs_all)))
    freqs = np.array([freqs_all[i] for i in freq_indices], dtype=float)
    print("Frequencias:", freqs)
    # ahora sí: NUM_POINTS consistente con lo que vas a barrer
    NUM_POINTS = len(freqs)

    # --------------- setup de arrays de resultados ---------------
    ganancias = np.zeros(NUM_POINTS, dtype=float)
    incerts = np.zeros(NUM_POINTS, dtype=float)
    phases = np.zeros(NUM_POINTS, dtype=float)
    incerts_phases = np.zeros(NUM_POINTS, dtype=float)
    estados = ["pendiente"] * NUM_POINTS

    # --------------- setup del osciloscopio ---------------
    time_base_inicial = 1.0 / freqs[0]
    base_dir = "/content/drive/MyDrive/SWEEP_MEDID/1kptos/"
    peak_strategy = InputPeakBinSelector(ignore_dc=True)



    # --------------- barrido en frecuencia ---------------
    for i, f in enumerate(freqs):
        meds_in = sorted({med for (ff, port, med) in src.files.keys() if ff == f and port == "IN"})
        meds_out = sorted({med for (ff, port, med) in src.files.keys() if ff == f and port == "OUT"})
        meds_ok = sorted(set(meds_in).intersection(meds_out))
        print(f"\n[{i + 1}/{NUM_POINTS}] Frecuencia = {f:.1f} Hz")
        ruidos_por_freq = list()
        if MEDICIONES_POR_FREQ is not None:
            meds_ok = meds_ok[:int(MEDICIONES_POR_FREQ)]
        # Configurar generador
        print(f"Seteando generador: f = {f:.1f} Hz, Vpp = {AMPLITUDE_VPP}")
        # Configurar timebase del osciloscopio según frecuencia

        time.sleep(2)  # dejar estabilizar

        fs = 50e3
        bloque = BloqueIO(frecuencia=float(f), nro_mediciones=MEDICIONES_POR_FREQ, bin_selector=peak_strategy)
        bloque.frecuencia = f

        estados[i] = "midiendo"
        # render_status(freqs, estados)

        for j in range(bloque.nro_mediciones):
            # Adquirir trazas
            f_in, fs_in, t_in, v_in = src.get_input(freq_idx=i, medicion=meds_ok[j])
            f_out, fs_out, t_out, v_out = src.get_output(freq_idx=i, medicion=meds_ok[j])
            amp_noise = 100
            noise_in = amp_noise * rng.normal(0.0, 0.01, len(v_in))
            noise_out = amp_noise * rng.normal(0.0, 0.01, len(v_out))

            bloque.measure(v_in, v_out, t_in, t_out, fs_in=fs, fs_out=fs)  # Probamos con la fs calculada, despues vemos que onda la fs del oscilo
            print(f"finalizada medicion [{j}/{bloque.nro_mediciones}] de la freq = {f:.1f} Hz [{i}/{NUM_POINTS}]")
            procesar_bloque(
                i,
                bloque,
                estados,
                ganancias,
                incerts,
                phases,
                incerts_phases,
            )
            print(f"finalizada medicion [{j}/{bloque.nro_mediciones}] de la freq = {f:.1f} Hz [{i}/{NUM_POINTS}]")
        print("")
        time.sleep(1)

    clear_output(wait=True)

    print(f"\nSweep terminado en {time.time() - t0:.1f} s")
    print("Barrido completado ✅")

    # ===================== RESULTADOS =====================




    csv_path = os.path.join(SAVE_PATH, "bode_data.csv")
    print("Datos guardados en:", csv_path)

    # ---- Gráfico de Magnitud ----
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6), dpi=140, sharex=True)

    ax1.semilogx(freqs, ganancias, label="Ganancia [dB]")
    ax1.fill_between(
        freqs,
        ganancias - incerts,
        ganancias + incerts,
        alpha=0.3,
        label="±σ (Rice) [dB]",
    )
    ax1.set_ylabel("Ganancia [dB]")
    ax1.grid(True, which="both")
    ax1.legend(loc="best")

    # ---- Gráfico de Fase ----
    phases_unwrapped = np.unwrap(phases)
    ax2.semilogx(freqs, phases_unwrapped, label="Fase [rad]")
    ax2.fill_between(
        freqs,
        phases_unwrapped - incerts_phases,
        phases_unwrapped + incerts_phases,
        alpha=0.3,
        label="±σ fase",
    )
    ax2.set_xlabel("Frecuencia [Hz]")
    ax2.set_ylabel("Fase [rad]")
    ax2.grid(True, which="both")
    ax2.legend(loc="best")
    ax2.set_xlim(freqs[0], freqs[-1])

    plt.tight_layout()
    plt.show()

    print("Incertidumbres de fase:", incerts_phases)

    return None





if __name__ == "__main__":
    print("Comenzando barrido de frecuencia...\n")

    df_result = run_sweep()
