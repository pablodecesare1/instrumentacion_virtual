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
import pyvisa as visa
import vxi11
from IPython.core.display_functions import clear_output

from InstVirtualLib.Sweep.Report_generator.Measurement_save import export_trace_to_csv
from InstVirtualLib.Sweep.SweepAnalisis.Sweep_clasess.BloqueIO import BloqueIO
from InstVirtualLib.Sweep.SweepAnalisis.Sweep_strategies import InputPeakBinSelector
from InstVirtualLib.Sweep.SweepAnalisis.Sweep_utils import procesar_bloque

sys.path.insert(0, "InstVirtualLib")
from InstVirtualLib.osciloscopios import RIGOL_DS2202              # noqa: E402
from InstVirtualLib.generadores_arbitrarios import Siglent1032X    # noqa: E402


# ====================== PARÁMETROS DE BARRIDO =========================================================================================
# ======================================================================================================================================
F_START = 20.0          # Hz
F_STOP = 20_000.0       # Hz
NUM_POINTS = 5          # cantidad de puntos del sweep
AMPLITUDE_VPP = 5.0     # Vpp
SAVE_PATH = "../../resultados_sweep"  # carpeta donde se guardan resultados
MEDICIONES_POR_FREQ = 3
# ======================================================================================================================================
# ====================== PARÁMETROS DE BARRIDO =========================================================================================


# ===================== FUNCIONES AUXILIARES ========================

def run_sweep(gen: Siglent1032X, scope: RIGOL_DS2202):
    """
        Ejecuta un barrido en frecuencia usando el generador y el osciloscopio.

        Devuelve un DataFrame con columnas:
          - freq_Hz
          - mag_dB
          - phase_deg
          - incert_dB
          - incert_phase_deg
        """
    print("Inicializando barrido...")
    print("Plataforma:", platform.platform())


    freqs = np.geomspace(F_START, F_STOP, NUM_POINTS)
    os.makedirs(SAVE_PATH, exist_ok=True)

    print("Inicializando barrido...")
    print("Plataforma:", platform.platform())

    t0 = time.time()

    # --------------- setup de arrays de resultados ---------------
    ganancias       = np.zeros_like(freqs, dtype=float)
    incerts         = np.zeros_like(freqs, dtype=float)
    phases          = np.zeros_like(freqs, dtype=float)
    incerts_phases  = np.zeros_like(freqs, dtype=float)
    ruidos          = np.zeros_like(freqs, dtype=float)
    estados         = ["pendiente"] * len(freqs)

    # --------------- setup del osciloscopio ---------------
    time_base_inicial = 1.0 / freqs[0]
    scope.set_BT(f"{time_base_inicial:.2f}")
    scope.set_chan_DIV(AMPLITUDE_VPP, 1)
    scope.set_chan_DIV(AMPLITUDE_VPP, 2)
    scope.set_memdepth("70000")

    peak_strategy = InputPeakBinSelector(ignore_dc=True)

    # --------------- barrido en frecuencia ---------------
    for i, f in enumerate(freqs):
        print(f"\n[{i + 1}/{NUM_POINTS}] Frecuencia = {f:.1f} Hz")

        # Configurar generador
        gen.senoidal(f, AMPLITUDE_VPP)
        print(f"Seteando generador: f = {f:.1f} Hz, Vpp = {AMPLITUDE_VPP}")
        gen.enable_output()
        ruidos_por_freq = list()

        # Configurar timebase del osciloscopio según frecuencia
        time_base = 1.0 / f
        scope.set_BT(f"{time_base:.6f}")

        time.sleep(2)  # dejar estabilizar



        fs = float(scope.get_samplerate())
        bloque = BloqueIO(
            frecuencia=float(f),
            nro_mediciones=MEDICIONES_POR_FREQ,
            bin_selector=peak_strategy,
        )
        bloque.frecuencia = f

        estados[i] = "midiendo"
        for j in range(bloque.nro_mediciones):
            t_in, x_in = scope.get_trace(1)
            t_out, x_out = scope.get_trace(2)

            bloque.measure(x_in, x_out, t_in, t_out, fs_in=fs, fs_out=fs)  # Probamos con la fs calculada, despues vemos que onda la fs del oscilo
            print(f"finalizada medicion [{j}/{bloque.nro_mediciones}] de la freq = {f:.1f} Hz [{i}/{NUM_POINTS}]")
            saveMeasurement(t_in, x_in, t_out, x_out, f, j)
            ruidos_por_freq.append(bloque.get_ruido("in"))
        procesar_bloque(
            i,
            bloque,
            estados,
            ganancias,
            incerts,
            phases,
            incerts_phases,
            ruidos,
            np.mean(ruidos_por_freq),
        )
        print("")
        time.sleep(1)

    gen.disable_output()
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
        color='red',
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
        color='red',
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

    return freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos


def saveMeasurement(t_in, v_in, t_out, v_out, freq, measurement):
    export_trace_to_csv(
        out_dir=SAVE_PATH,
        time_s=t_in,
        voltage_v=v_in,
        port="IN",
        freq_hz=freq,
        measurement_idx=measurement + 1,
    )

    export_trace_to_csv(
        out_dir=SAVE_PATH,
        time_s=t_out,
        voltage_v=v_out,
        port="OUT",
        freq_hz=freq,
        measurement_idx=measurement + 1,
    )


def saveResults():
    return


def init_instruments():
    """Inicializa VISA + VXI11 y devuelve (generador, osciloscopio)."""
    print("Inicializando instrumentos...")
    print("Plataforma:", platform.platform())

    rm1 = visa.ResourceManager()
    rm2 = visa.ResourceManager()

    # Osciloscopio Rigol por VXI11
    vxi11_instr = vxi11.Instrument("192.168.0.100")  # TODO: parametrizar IP
    scope = RIGOL_DS2202(handler=None, VXI11=vxi11_instr)

    # Generador Siglent por VISA TCPIP
    gen_handler = rm2.open_resource("TCPIP::192.168.0.101::5025::INSTR")
    gen = Siglent1032X(gen_handler)

    return gen, scope

"""
if __name__ == "__main__":
    print("Comenzando barrido de frecuencia...\n")
    generador, osciloscopio = init_instruments()
    freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos = run_sweep(generador, osciloscopio)
    assets_dir = "./Report_generator/assets"
    createReport(freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos, assets_dir)
"""
