import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import socket
import ipaddress
import time
import csv

# ==========================
# CONFIGURACIÓN
# ==========================

PUERTOS_SCPI = [5025, 5555, 4000, 3000]
PUERTO_PING = 80
TIMEOUT = 0.4
MAX_HILOS = 80

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
    return ipaddress.IPv4Network(ip + "/24", strict=False)


def resolver_nombre(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None


def ip_activa(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        resultado = sock.connect_ex((ip, PUERTO_PING))
        sock.close()
        return resultado == 0
    except:
        return False


def consultar_idn(ip):
    for puerto in PUERTOS_SCPI:
        try:
            with socket.create_connection((ip, puerto), timeout=TIMEOUT) as s:
                s.sendall(b"*IDN?\n")
                respuesta = s.recv(1024).decode().strip()
                if respuesta:
                    return respuesta, puerto
        except:
            continue
    return None, None


# ==========================
# VARIABLES GLOBALES
# ==========================

resultados_totales = []
instrumentos_detectados = []

# ==========================
# ESCANEO
# ==========================

def escanear_red():

    lista_dispositivos.delete(0, tk.END)
    lista_instrumentos.delete(0, tk.END)
    progress["value"] = 0

    resultados_totales.clear()
    instrumentos_detectados.clear()

    red = obtener_red_local()
    ips = list(red.hosts())
    total = len(ips)
    contador = 0
    lock = threading.Lock()

    def worker(ip):
        nonlocal contador
        ip = str(ip)

        nombre = resolver_nombre(ip)

        if ip_activa(ip):

            idn, puerto = consultar_idn(ip)

            if idn:
                texto = f"🟢 {ip} | SCPI | Puerto {puerto} | {idn}"
                instrumentos_detectados.append((ip, puerto, idn))
            else:
                if nombre:
                    texto = f"🟡 {ip} | Activo | {nombre}"
                else:
                    texto = f"🟡 {ip} | Activo | Desconocido"

            resultados_totales.append(texto)

        with lock:
            contador += 1
            progress["value"] = (contador / total) * 100

    threads = []

    for ip in ips:
        t = threading.Thread(target=worker, args=(ip,))
        t.start()
        threads.append(t)

        while threading.active_count() > MAX_HILOS:
            time.sleep(0.01)

    for t in threads:
        t.join()

    mostrar_resultados()


def mostrar_resultados():

    lista_dispositivos.delete(0, tk.END)
    lista_instrumentos.delete(0, tk.END)

    if not resultados_totales:
        lista_dispositivos.insert(tk.END, "No se encontraron IP activas.")
        return

    for r in sorted(resultados_totales):
        lista_dispositivos.insert(tk.END, r)

    if instrumentos_detectados:
        for ip, puerto, idn in instrumentos_detectados:
            lista_instrumentos.insert(
                tk.END, f"{ip} | Puerto {puerto} | {idn}"
            )
    else:
        lista_instrumentos.insert(tk.END, "No se detectaron instrumentos SCPI.")


def iniciar_escaneo():
    threading.Thread(target=escanear_red, daemon=True).start()


# ==========================
# EXPORTAR CSV
# ==========================

def exportar_csv():
    if not resultados_totales:
        messagebox.showwarning("Aviso", "No hay datos para exportar.")
        return

    archivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")]
    )

    if archivo:
        with open(archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Resultado"])
            for r in resultados_totales:
                writer.writerow([r])

        messagebox.showinfo("Exportado", "Archivo CSV guardado correctamente.")


# ==========================
# GUI
# ==========================

root = tk.Tk()
root.title("Sistema Profesional de Detección SCPI")
root.geometry("1000x700")

titulo = tk.Label(root,
                  text="Detector Profesional de Instrumentos SCPI",
                  font=("Arial", 16, "bold"))
titulo.pack(pady=10)

frame_principal = tk.Frame(root)
frame_principal.pack(pady=10)

# -------------------------
# LISTA DISPOSITIVOS
# -------------------------

frame_izq = tk.Frame(frame_principal)
frame_izq.pack(side="left", padx=20)

tk.Label(frame_izq,
         text="Dispositivos detectados en red",
         font=("Arial", 12, "bold")).pack()

lista_dispositivos = tk.Listbox(frame_izq, width=70, height=25)
lista_dispositivos.pack()

# -------------------------
# LISTA INSTRUMENTOS
# -------------------------

frame_der = tk.Frame(frame_principal)
frame_der.pack(side="right", padx=20)

tk.Label(frame_der,
         text="Instrumentos SCPI Detectados",
         font=("Arial", 12, "bold"),
         fg="green").pack()

lista_instrumentos = tk.Listbox(frame_der, width=60, height=25)
lista_instrumentos.pack()

# -------------------------
# BARRA DE PROGRESO
# -------------------------

progress = ttk.Progressbar(root,
                           orient="horizontal",
                           length=800,
                           mode="determinate")
progress.pack(pady=15)

# -------------------------
# BOTONES
# -------------------------

frame_botones = tk.Frame(root)
frame_botones.pack(pady=10)

tk.Button(frame_botones,
          text="Escanear Red Completa",
          bg="blue",
          fg="white",
          font=("Arial", 11),
          command=iniciar_escaneo).pack(side="left", padx=15)

tk.Button(frame_botones,
          text="Exportar Resultados CSV",
          bg="green",
          fg="white",
          font=("Arial", 11),
          command=exportar_csv).pack(side="left", padx=15)

tk.Button(frame_botones,
          text="Salir",
          bg="red",
          fg="white",
          font=("Arial", 11),
          command=root.destroy).pack(side="left", padx=15)

root.mainloop()
