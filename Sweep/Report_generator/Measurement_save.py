# export_trace.py
# -*- coding: utf-8 -*-

import os
import pandas as pd
from typing import Sequence, Union

Number = Union[int, float]


def export_trace_to_csv(
    out_dir: str,
    time_s: Sequence[Number],
    voltage_v: Sequence[Number],
    port: str,
    freq_hz: Number,
    measurement_idx: int,
) -> str:
    """
    Guarda una traza en un CSV con formato:
        <FREQ>-<NroMedicion>-<IN/OUT>.csv

    Ejemplo:
        20_000-1-OUT.csv

    Parámetros
    ----------
    out_dir : str
        Carpeta donde se va a guardar el archivo.
    time_s : array-like
        Vector de tiempo en segundos.
    voltage_v : array-like
        Vector de tensión en voltios.
    port : str
        "IN" o "OUT".
    freq_hz : float
        Frecuencia en Hz.
    measurement_idx : int
        Número de medición (1, 2, 3, ...).

    Devuelve
    --------
    str
        Ruta completa del archivo CSV generado.
    """
    os.makedirs(out_dir, exist_ok=True)

    port = port.upper()
    if port not in ("IN", "OUT"):
        raise ValueError(f"port inválido: {port}. Esperaba 'IN' o 'OUT'.")

    # 20000 -> "20_000"
    freq_str = f"{int(round(freq_hz)):,}".replace(",", "_")

    filename = f"{freq_str}-{measurement_idx}-{port}.csv"
    filepath = os.path.join(out_dir, filename)

    df = pd.DataFrame(
        {
            "time_s": time_s,
            "voltage_V": voltage_v,
        }
    )
    df.to_csv(filepath, index=False)

    return filepath
