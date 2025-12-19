from IPython.display import clear_output

from InstVirtualLib.Sweep.SweepAnalisis.Sweep_clasess.BloqueIO import BloqueIO
from InstVirtualLib.Sweep.SweepAnalisis.Sweep_strategies import BinSelectorStrategy




# -------------------------
# Render / procesado
# -------------------------
def render_status(frecuencias, estados):
    clear_output(wait=True)
    print("Estado barrido de frecuencias")
    print("-" * 45)
    print(f"{'idx':>3} | {'freq [Hz]':>10} | {'estado':>12}")
    print("-" * 45)
    for i, (f, st) in enumerate(zip(frecuencias, estados)):
        print(f"{i:3d} | {f:10.2f} | {st:>12}")
    print("-" * 45)

def procesar_bloque(
    idx,
    bloque: BloqueIO,
    estados,
    ganancias,
    incerts,
    phases,
    incerts_phases,
    ruidos,
    ruido_mean,
    selector: BinSelectorStrategy | None = None
):
    """
    Corre Bode módulo + fase con el selector indicado (o el default del bloque).
    """
    estados[idx] = "procesando"

    G_db, U_G_db = bloque.inform_module_bode(selector=selector, plot=False)
    fase, U_fase, fbin, meta = bloque.inform_phase_bode(selector=selector, plot=False)

    ganancias[idx] = G_db
    phases[idx] = fase
    incerts[idx] = U_G_db
    incerts_phases[idx] = U_fase
    ruidos[idx] = ruido_mean
    estados[idx] = "completado"
    return idx
