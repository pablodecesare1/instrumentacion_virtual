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

    os.makedirs(out_dir, exist_ok=True)

    port = port.upper()
    if port not in ("IN", "OUT"):
        raise ValueError(f"port inválido: {port}. Esperaba 'IN' o 'OUT'.")

    # ==========================================
    # freq en Hz → formateo "<entero>_000"
    # ej: 20000 → "20000_000"
    #     112468 → "112468_000"
    # ==========================================

    # Paso 1: convertir a string con 3 decimales en kHz
    freq_khz = freq_hz / 1000.0               # 20000 Hz → 20.000
    freq_khz_str = f"{freq_khz:.3f}"          # siempre 3 decimales

    # Paso 2: eliminar "." y formato miles
    ent = freq_khz_str.replace(".", "").replace(",", "")

    # Paso 3: agregar _000 (los Hz decimales)
    freq_str = f"{ent}_000"

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
