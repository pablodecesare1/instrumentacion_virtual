# =======================================================================================================
# BloqueIO => Clase que reune todas las distintas mediciones sobre un cuadripolo
# =======================================================================================================
import numpy as np
from matplotlib import pyplot as plt
from scipy import special

from Sweep.SweepAnalisis.Sweep_clasess.FFT_buff import FFT
from Sweep.SweepAnalisis.Sweep_clasess.Signal import Signal
from Sweep.SweepAnalisis.Sweep_strategies import TargetFrequencyBinSelector, BinSelectorStrategy


class BloqueIO:
    def __init__(self, frecuencia=None, nro_mediciones=20, bin_selector=None, ventana_fft="flattop"):
        self.frecuencia = frecuencia
        self.nro_mediciones = nro_mediciones
        self.mediciones = []
        self.bin_selector = bin_selector or TargetFrequencyBinSelector()
        self.ventana_fft = ventana_fft

    def measure(self, x_in, x_out, t_in, t_out, fs_in=None, fs_out=None):
        sig = Signal(x_in=x_in, x_out=x_out, t_in=t_in, t_out=t_out)
        sig.calculate_fft(fs_in=fs_in, fs_out=fs_out, ventana=self.ventana_fft)
        self.mediciones.append(sig)

    def set_entrada(self, idx, signal: Signal):
        if not (0 <= idx < self.nro_mediciones):
            raise IndexError(f"Índice fuera de rango: 0..{self.nro_mediciones - 1}")
        self.mediciones[idx] = signal

    def set_bin_selector(self, selector: BinSelectorStrategy):
        self.bin_selector = selector

    def _stack_time_signals(self, entrada: str = "in"):
        entrada = entrada.lower()
        xs = [s.x_in if entrada == "in" else s.x_out for s in self.mediciones]

        if any(x.size == 0 for x in xs):
            raise ValueError("Hay mediciones sin datos en tiempo.")
        if len({x.size for x in xs}) != 1:
            raise ValueError("Todas las mediciones deben tener la misma longitud N.")
        return np.vstack(xs)

    def _stack_ffts(self, entrada: str = "in"):
        """
        Devuelve (ffts, freqs, N_time, coherent_gain)
        """
        entrada = entrada.lower()
        if entrada == "in":
            ffts = [s.fft_in.valores for s in self.mediciones]
            ref = self.mediciones[0].fft_in
        elif entrada == "out":
            ffts = [s.fft_out.valores for s in self.mediciones]
            ref = self.mediciones[0].fft_out
        else:
            raise ValueError("entrada debe ser 'in' o 'out'")

        if any(F.size == 0 for F in ffts):
            raise ValueError("Hay mediciones sin FFT calculada.")
        if ref.freqs.size == 0:
            raise ValueError("Faltan freqs en la primera medición.")
        if len({F.size for F in ffts}) != 1:
            raise ValueError("Todas las FFT deben tener igual cantidad de bins.")

        return np.vstack(ffts), ref.freqs, ref.N_time, ref.coherent_gain

    def get_ruido(self, entrada="in"):
        xs = self._stack_time_signals(entrada)
        mean = xs.mean(axis=0)
        sigmas = np.std(xs - mean, axis=1, ddof=1)
        return float(sigmas.mean())

    def get_fft_prom(self, entrada="in") -> FFT:
        ffts, freqs, N_time, cg = self._stack_ffts(entrada)
        return FFT(freqs=freqs, valores=ffts.mean(axis=0), N_time=N_time, coherent_gain=cg)

    def calculate_rice(self, entrada="in", fft_norm="none", de_normalize=False):
        N = self._stack_time_signals(entrada=entrada).shape[1]
        sigma = UncertAnalyzer.sigma_R_from_block(self, entrada=entrada, fft_norm=fft_norm)
        if de_normalize:
            # pasar a Vpk con coher. gain
            fft_prom = self.get_fft_prom(entrada)
            cg = max(fft_prom.coherent_gain, 1e-300)
            return sigma * (2.0 / N) * (1.0 / cg)
        return sigma

    def _select_idx(self, selector=None):
        sel = selector or self.bin_selector
        fft_in = self.get_fft_prom("in")
        fft_out = self.get_fft_prom("out")
        return sel.select_idx(self, fft_in, fft_out)  # (idx, meta)

    def calcular_ganancia(self, entrada="in", selector=None, plot=False):
        """
        Devuelve:
          - A_vpk, sigma_vpk, f_bin, meta
        """
        fft_prom = self.get_fft_prom(entrada=entrada)

        idx, meta = self._select_idx(selector=selector)
        f_bin = float(fft_prom.freqs[idx])

        # amplitud Vpk consistente con ventana
        A_spec = fft_prom.amp_vpk()
        A = float(A_spec[idx])

        # sigma Rice (sobre |FFT| cruda) -> Vpk con 2/N y coherent_gain
        sigma_R = self.calculate_rice(entrada=entrada)  # array por bin (|FFT| cruda)
        cg = max(fft_prom.coherent_gain, 1e-300)
        sA = float((2.0 / fft_prom.N_time) * (sigma_R[idx] / cg))

        if plot:
            vals_plot = A_spec.copy()
            if vals_plot.size:
                vals_plot[0] = 0

            plt.figure(figsize=(7, 3), dpi=140)
            plt.plot(fft_prom.freqs, vals_plot)
            if self.frecuencia is not None:
                plt.axvline(self.frecuencia, linestyle="--", alpha=0.6, label="f_obj")
            plt.axvline(f_bin, linestyle="-", alpha=0.85, label=f"f_bin ({meta['mode']})")
            plt.title(f"FFT {entrada.upper()} (Vpk) | f_bin={f_bin:.3f} Hz")
            plt.xlabel("Frecuencia [Hz]")
            plt.ylabel("Amplitud [V pico]")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()

        return A, sA, f_bin, meta

    def inform_module_bode(self, selector=None, plot=False):
        Ain, sAin, fbin_in, meta_in = self.calcular_ganancia("in", selector=selector, plot=False)
        Aout, sAout, fbin_out, meta_out = self.calcular_ganancia("out", selector=selector, plot=False)

        G_db = Signal.calculate_db(Aout) - Signal.calculate_db(Ain)

        eps = 1e-300
        u_G_db = (20.0 / np.log(10.0)) * np.sqrt(
            (sAout / max(Aout, eps)) ** 2 +
            (sAin / max(Ain, eps)) ** 2
        )
        U_G_db = 2.0 * u_G_db

        if plot:
            print(
                f"[module] mode={meta_in['mode']} "
                f"fbin_in={fbin_in:.4f} fbin_out={fbin_out:.4f} "
                f"G_db={G_db:.3f} ± {U_G_db:.3f} dB"
            )

        return G_db, U_G_db

    def inform_phase_bode(self, selector=None, plot=False):
        """
        Fase = angle(FFT_out/FFT_in) en el bin elegido.
        Incertidumbre: suma cuadrática de varianzas (k=2).
        """
        fft_in = self.get_fft_prom("in")
        fft_out = self.get_fft_prom("out")

        idx, meta = self._select_idx(selector=selector)

        Zin = fft_in.valores[idx]
        Zout = fft_out.valores[idx]
        H = Zout / (Zin if Zin != 0 else (1e-300 + 0j))
        fase = float(np.angle(H))

        N_in = self._stack_time_signals("in").shape[1]
        N_out = self._stack_time_signals("out").shape[1]
        sigma_t_in = self.get_ruido("in")
        sigma_t_out = self.get_ruido("out")

        # var(phi) por canal
        var_in = UncertAnalyzer.phase_var_from_time_noise(Zin, sigma_t_in, N_in)
        var_out = UncertAnalyzer.phase_var_from_time_noise(Zout, sigma_t_out, N_out)

        U_fase = 2.0 * np.sqrt(max(var_in + var_out, 0.0))

        if plot:
            print(
                f"[phase] mode={meta['mode']} "
                f"f_bin_in={meta['f_bin_in']:.4f} rad_phase={fase:.4f} ± {U_fase:.4f}"
            )

        return fase, U_fase, float(fft_in.freqs[idx]), meta


# ==================================================
# UncertAnalyzer (Rice + fase)
# ==================================================
class UncertAnalyzer:
    """
    Rice sobre el módulo de FFT promedio (asumiendo ruido gaussiano).
    NOTA: esto asume la relación sigma_fft ~ sqrt(N/2)*sigma_t para FFT cruda sin normalizar.
    Si usás ventanas, deberías corregir por ENBW/ganancia coherente.
    """

    @staticmethod
    def phase_var_from_time_noise(Zbin, sigma_t, N):
        """
        Var(phi) aprox con ruido pequeño:
          sigma_f ≈ sqrt(N/2) * sigma_t   (FFT cruda)
          var(phi) ≈ sigma_f^2 / (2 |Z|^2)
        """
        Zmag2 = float(np.abs(Zbin) ** 2)
        if Zmag2 <= 0:
            return np.inf
        sigma_f = np.sqrt(N / 2.0) * sigma_t
        return (sigma_f ** 2) / (2.0 * Zmag2)

    @staticmethod
    def _get_l_1_2(v, sigma):
        x = - (v ** 2) / (2.0 * sigma ** 2)
        return special.eval_laguerre(0.5, x)

    @classmethod
    def _get_variance_rice(cls, v, sigma):
        L = cls._get_l_1_2(v, sigma)
        return 2.0 * (sigma ** 2) + (v ** 2) - (np.pi * (sigma ** 2) / 2.0) * (L ** 2)

    @staticmethod
    def _get_sigma_fft(sigma_t, N, fft_norm="none"):
        if fft_norm != "none":
            raise NotImplementedError("Solo fft_norm='none' en esta implementación.")
        return np.sqrt(N / 2.0) * sigma_t

    @classmethod
    def sigma_R_from_block(cls, bloque, entrada="in", fft_norm="none"):
        sigma_t = bloque.get_ruido(entrada=entrada)

        ffts, freqs, N_time, cg = bloque._stack_ffts(entrada)  # 👈 actualizado
        xs = bloque._stack_time_signals(entrada)
        M, N = xs.shape

        sigma_fft_1 = cls._get_sigma_fft(sigma_t, N, fft_norm=fft_norm)
        sigma_fft = sigma_fft_1 / np.sqrt(M)

        F_central = ffts.mean(axis=0)
        v = np.abs(F_central)

        if sigma_fft == 0:
            return np.zeros_like(v)

        var = cls._get_variance_rice(v, sigma_fft)
        var = np.maximum(var, 0.0)
        return np.sqrt(var)

