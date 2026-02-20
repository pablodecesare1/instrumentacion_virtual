from pathlib import Path
from InstVirtualLib.Sweep.Report_generator.Report_maker import createReport
from InstVirtualLib.Sweep.SweepConfig import SweepConfig
from InstVirtualLib.Sweep.Sweeper import init_instruments, run_sweep

def run_measurement(params: dict):
    """
    params esperado:
      ip_osc, ip_gen, f_inicio, f_stop, puntos, mediciones, amplitud
    """
    config = SweepConfig(
        F_START=params["f_inicio"],
        F_STOP=params["f_stop"],
        NUM_POINTS=params["puntos"],
        AMPLITUDE_VPP=params["amplitud"],
        SAVE_PATH=Path("../../mis_resultados"),
        MEDICIONES_POR_FREQ=params["mediciones"],
        IP_GEN=params["ip_gen"],
        IP_SCOPE=params["ip_osc"],
        MEM_DEPTH=7000,
    )

    generador, osciloscopio = init_instruments(config.IP_GEN, config.IP_SCOPE)

    freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos = run_sweep(
        generador, osciloscopio, config=config
    )

    assets_dir = "./Report_generator/assets"
    createReport(freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos, assets_dir)