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
from InstVirtualLib.Sweep.SweepConfig import SweepConfig

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

import numpy as np

def set_output_div(gen: Siglent1032X, scope: RIGOL_DS2202, ch=2,
                   method="percentile", headroom=1.25, q=99.9, min_div=0.02):
    t_out, x_out = scope.get_trace(ch)
    x_out = np.asarray(x_out)

    # estimación de pico robusta
    x0 = x_out - np.mean(x_out)  # saco DC
    if method == "rms":
        vrms = np.sqrt(np.mean(x0**2))
        vpk = np.sqrt(2) * vrms
    else:  # "percentile"
        vpk = np.percentile(np.abs(x0), q)

    # DIV: querés que el pico ocupe ~2 divisiones (como vos)
    div = (vpk / 2.0) * headroom
    div = max(div, min_div)

    scope.set_chan_DIV(div, ch)


# ===================== FUNCIONES AUXILIARES ========================

def run_sweep(gen: Siglent1032X, scope: RIGOL_DS2202, config:SweepConfig = SweepConfig()):
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


    freqs = np.geomspace(config.F_START, config.F_STOP, config.NUM_POINTS)
    os.makedirs(config.SAVE_PATH, exist_ok=True)

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
    scope.set_chan_DIV(config.AMPLITUDE_VPP/4, 1)
    scope.set_chan_DIV(config.AMPLITUDE_VPP/4, 2)
    ################## SIN PROBAR ##################
    scope.set_trigger_level("0")
    scope.set_trigger_edge_source(1)
    scope.set_channel_prob(canal = 1)
    scope.set_channel_prob(canal = 2)
    scope.set_trigger_coup_AC()
    scope.set_chan_OFFSET("0",1)
    scope.set_chan_OFFSET("0",2)
    ################## SIN PROBAR ##################

    scope.set_memdepth("7000")

    peak_strategy = InputPeakBinSelector(ignore_dc=True)
    time.sleep(5)
    # --------------- barrido en frecuencia ---------------
    for i, f in enumerate(freqs):
        print(f"\n[{i + 1}/{config.NUM_POINTS}] Frecuencia = {f:.1f} Hz")

        # Configurar generador
        gen.senoidal(f, config.AMPLITUDE_VPP)
        print(f"Seteando generador: f = {f:.1f} Hz, Vpp = {config.AMPLITUDE_VPP}")
        gen.enable_output()
        ruidos_por_freq = list()

        # Configurar timebase del osciloscopio según frecuencia
        time_base = 1.0 / f
        scope.set_BT(f"{time_base*1:.6f}")

        time.sleep(1)  # dejar estabilizar
        set_output_div(gen, scope)


        fs = float(scope.get_samplerate())
        bloque = BloqueIO(
            frecuencia=float(f),
            nro_mediciones=config.MEDICIONES_POR_FREQ,
            bin_selector=peak_strategy,
        )
        bloque.frecuencia = f

        estados[i] = "midiendo"
        for j in range(bloque.nro_mediciones):
            t_in, x_in = scope.get_trace(1)
            t_out, x_out = scope.get_trace(2)

            bloque.measure(x_in, x_out, t_in, t_out, fs_in=fs, fs_out=fs)  # Probamos con la fs calculada, despues vemos que onda la fs del oscilo
            print(f"finalizada medicion [{j}/{bloque.nro_mediciones}] de la freq = {f:.1f} Hz [{i}/{config.NUM_POINTS}]")
            saveMeasurement(t_in, x_in, t_out, x_out, f, j, config)
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
        yield i
        print("")

    gen.disable_output()
    clear_output(wait=True)

    print(f"\nSweep terminado en {time.time() - t0:.1f} s")
    print("Barrido completado ✅")

    # ===================== RESULTADOS =====================

    csv_path = os.path.join(config.SAVE_PATH, "bode_data.csv")
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
    ax2.set_ylim(-np.pi/2,0)
    ax2.grid(True, which="both")
    ax2.legend(loc="best")
    ax2.set_xlim(freqs[0], freqs[-1])

    plt.tight_layout()
    plt.show()

    print("Incertidumbres de fase:", incerts_phases)

    return freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos


def saveMeasurement(t_in, v_in, t_out, v_out, freq, measurement, config:SweepConfig = SweepConfig()):
    return


def saveResults():
    return


def init_instruments(ip_gen="192.168.0.100", ip_osc="192.168.0.101"):
    """Inicializa VISA + VXI11 y devuelve (generador, osciloscopio)."""
    print("Inicializando instrumentos...")
    print("Plataforma:", platform.platform())

    rm1 = visa.ResourceManager()
    rm2 = visa.ResourceManager()

    # Osciloscopio Rigol por VXI11
    vxi11_instr = vxi11.Instrument(ip_osc)  # TODO: parametrizar IP
    scope = RIGOL_DS2202(handler=None, VXI11=vxi11_instr)

    # Generador Siglent por VISA TCPIP
    gen_handler = rm2.open_resource("TCPIP::"+ ip_gen+"::INSTR")
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
