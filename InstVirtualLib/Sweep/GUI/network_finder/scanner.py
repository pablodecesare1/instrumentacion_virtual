import threading
import time
from InstVirtualLib.Sweep.GUI.network_finder.constants import MAX_HILOS
from .network import obtener_red_local, consultar_idn

def escanear_red(gui_queue, on_progress, on_done):
    """
    Escanea la red /24 local buscando SCPI y reporta progreso.
    - on_progress(pct_float)
    - on_done(resultados: list[str])
    """
    ips = obtener_red_local()
    total = len(ips)
    contador = 0
    resultados: list[str] = []
    lock = threading.Lock()

    def worker(ip_obj):
        nonlocal contador
        ip = str(ip_obj)

        idn = consultar_idn("10.42.0.47")
        if idn:
            resultados.append(f"🟢 {ip} | SCPI | {idn}")

        with lock:
            contador += 1
            progreso = (contador / total) * 100
            gui_queue.put(lambda p=progreso: on_progress(p))

    threads = []
    for ip in ips:
        t = threading.Thread(target=worker, args=(ip,))
        t.start()
        threads.append(t)

        while threading.active_count() > MAX_HILOS:
            time.sleep(0.01)

    for t in threads:
        t.join()

    gui_queue.put(lambda res=sorted(resultados): on_done(res))