import os, re, glob
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod


class SignalSource(ABC):
    @abstractmethod
    def get_input(self, **kwargs):
        pass

    @abstractmethod
    def get_output(self, **kwargs):
        pass


class CsvSignalSource(SignalSource):
    _PATTERN = re.compile(
        r'^(?P<freq>\d+_\d+)-(?P<med>\d+)-(?P<port>[A-Za-z]+)\.csv$',
        re.IGNORECASE
    )

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.files, self.freqs = self._index_files()

    def _index_files(self):
        files = {}
        freqs = set()

        for path in glob.glob(os.path.join(self.base_dir, "*.csv")):
            name = os.path.basename(path)
            m = self._PATTERN.match(name)
            if not m:
                continue

            freq = float(m.group("freq").replace("_", "."))
            med  = int(m.group("med"))
            port = m.group("port").upper()

            files[(freq, port, med)] = path
            freqs.add(freq)

        return files, sorted(freqs)

    def _read(self, path):
        df = pd.read_csv(path)
        t = df.iloc[:, 0].to_numpy(float)
        v = df.iloc[:, 1].to_numpy(float)

        # OJO: si t viene en microsegundos/segundos, esto cambia fs (pero es correcto)
        dt = np.diff(t)
        dt_med = np.median(dt) if dt.size else np.nan
        if not np.isfinite(dt_med) or dt_med <= 0:
            raise ValueError(f"No puedo inferir fs: dt_med inválido en {os.path.basename(path)}")

        fs = 1.0 / dt_med
        return t, v, fs

    def get_input(self, freq_idx: int, medicion: int):
        return self._get(freq_idx, medicion, "IN")

    def get_output(self, freq_idx: int, medicion: int):
        return self._get(freq_idx, medicion, "OUT")

    def get_frequencies(self):
        return self.freqs.copy()

    def _get(self, freq_idx, medicion, port):
        if freq_idx < 0 or freq_idx >= len(self.freqs):
            raise IndexError(f"freq_idx fuera de rango (0..{len(self.freqs)-1})")

        freq_hz = self.freqs[freq_idx]
        key = (freq_hz, port, medicion)
        if key not in self.files:
            raise FileNotFoundError(
                f"No existe freq_idx={freq_idx} ({freq_hz} Hz) – med {medicion} – {port}"
            )

        t, v, fs = self._read(self.files[key])
        return freq_hz, fs, t, v