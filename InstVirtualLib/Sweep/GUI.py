import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import ipaddress
import time
import queue
from pathlib import Path

from InstVirtualLib.Sweep.Report_generator.Report_maker import createReport
from InstVirtualLib.Sweep.SweepConfig import SweepConfig
from InstVirtualLib.Sweep.Sweeper import init_instruments, run_sweep

# ==========================
# CONFIGURACIÓN
# ==========================

PUERTO_SCPI = 5025
TIMEOUT = 0.3
MAX_HILOS = 100

cola_gui = queue.Queue()

# ==========================
# UTILIDADES RED
# ==========================

def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def obtener_red_local():
    ip = obtener_ip_local()
    return list(ipaddress.IPv4Network(ip + "/24", strict=False).hosts())


def consultar_idn(ip):
    try:
        with socket.create_connection((ip, PUERTO_SCPI), timeout=TIMEOUT) as s:
            s.sendall(b"*IDN?\n")
            return s.recv(1024).decode().strip()
    except:
        return None


def enviar_scpi(ip, comando):
    try:
        with socket.create_connection((ip, PUERTO_SCPI), timeout=2) as s:
            s.sendall((comando + "\n").encode())
            return s.recv(4096).decode().strip()
    except Exception as e:
        return None


# ==========================
# ACTUALIZADOR GUI
# ==========================

def procesar_cola():
    try:
        while True:
            funcion = cola_gui.get_nowait()
            funcion()
    except queue.Empty:
        pass
    root.after(50, procesar_cola)


# ==========================
# ESCANEO RÁPIDO
# ==========================

def escanear_red():

    ips = obtener_red_local()
    total = len(ips)
    contador = 0
    resultados = []

    lock = threading.Lock()

    def worker(ip):
        nonlocal contador
        ip = str(ip)

        idn = consultar_idn(ip)

        if idn:
            resultados.append(f"🟢 {ip} | SCPI | {idn}")

        with lock:
            contador += 1
            progreso = (contador / total) * 100
            cola_gui.put(lambda p=progreso: progress.configure(value=p))

    threads = []

    for ip in ips:
        t = threading.Thread(target=worker, args=(ip,))
        t.start()
        threads.append(t)

        while threading.active_count() > MAX_HILOS:
            time.sleep(0.01)

    for t in threads:
        t.join()

    cola_gui.put(lambda: actualizar_lista(resultados))


def actualizar_lista(resultados):
    lista_ips.delete(0, tk.END)

    if not resultados:
        lista_ips.insert(tk.END, "No se detectaron instrumentos SCPI.")
    else:
        for r in sorted(resultados):
            lista_ips.insert(tk.END, r)

    progress["value"] = 100


def escaneo_en_hilo():
    progress["value"] = 0
    lista_ips.delete(0, tk.END)
    threading.Thread(target=escanear_red, daemon=True).start()


# ==========================
# MEDICIÓN FUNCIONAL
# ==========================

def medicion_en_hilo():
    try:
        ip_osc = entry_ip_osc.get().strip()
        ip_gen = entry_ip_gen.get().strip()

        f_inicio = float(entry_f_inicio.get())
        f_stop = float(entry_f_stop.get())
        puntos = int(entry_puntos.get())
        mediciones = int(entry_mediciones.get())
        amplitud = int(entry_amplitud.get())

        if not ip_osc or not ip_gen:
            cola_gui.put(lambda: messagebox.showerror("Error", "Ingrese IP válidas"))
            return
########################################################################################################################
        config = SweepConfig(
            F_START=f_inicio,
            F_STOP=f_stop,
            NUM_POINTS=puntos,
            AMPLITUDE_VPP=amplitud,
            SAVE_PATH=Path("../../mis_resultados"),
            MEDICIONES_POR_FREQ=mediciones,
            IP_GEN=ip_gen,
            IP_SCOPE=ip_osc,
            MEM_DEPTH=7000
        )

        generador, osciloscopio = init_instruments(config.IP_GEN, config.IP_SCOPE)
        freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos = run_sweep(generador, osciloscopio, config=config)
        assets_dir = "./Report_generator/assets"
        createReport(freqs, ganancias, incerts, phases_unwrapped, incerts_phases, ruidos, assets_dir)
########################################################################################################################
        cola_gui.put(lambda: messagebox.showinfo("Medición", "Medición finalizada correctamente"))

    except Exception as e:
        cola_gui.put(lambda err=str(e): messagebox.showerror("Error", err))




def iniciar_medicion():
    progress["value"] = 0

    threading.Thread(target=medicion_en_hilo, daemon=True).start()


# ==========================
# GUI
# ==========================

root = tk.Tk()
root.title("Sistema de Medición Profesional")
root.geometry("700x750")

def crear_label_entry(texto):
    tk.Label(root, text=texto).pack()
    entry = tk.Entry(root)
    entry.pack()
    return entry


entry_f_inicio = crear_label_entry("Frecuencia inicio (Hz)")
entry_f_stop = crear_label_entry("Frecuencia stop (Hz)")
entry_puntos = crear_label_entry("Número de puntos")
entry_mediciones = crear_label_entry("Mediciones por frecuencia")
entry_ip_osc = crear_label_entry("IP Osciloscopio")
entry_ip_gen = crear_label_entry("IP Generador")
entry_amplitud = crear_label_entry("Amplitud Vpp")

tk.Label(root, text="Instrumentos SCPI detectados").pack(pady=10)

lista_ips = tk.Listbox(root, width=100, height=15)
lista_ips.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress.pack(pady=15)

tk.Button(root,
          text="Buscar Instrumentos SCPI",
          bg="blue",
          fg="white",
          command=escaneo_en_hilo).pack(pady=5)

tk.Button(root,
          text="Iniciar Medición",
          bg="green",
          fg="white",
          command=iniciar_medicion).pack(pady=5)

procesar_cola()
root.mainloop()
