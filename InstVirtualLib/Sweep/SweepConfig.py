from dataclasses import dataclass
from pathlib import Path

from InstVirtualLib.generadores_arbitrarios import generador_arbitrario
from InstVirtualLib.osciloscopios import osciloscopio


@dataclass
class SweepConfig:
    F_START: float = 20.0
    F_STOP: float = 20_000.0
    NUM_POINTS: int = 5
    AMPLITUDE_VPP: float = 5.0
    SAVE_PATH: Path = Path("../../resultados_sweep")
    MEDICIONES_POR_FREQ: int = 3
    IP_GEN: str = "192.168.0.101"
    IP_SCOPE: str = "192.168.0.100"
    MEM_DEPTH: int = 70_000
    OSC: osciloscopio = None
    GEN: generador_arbitrario = None
