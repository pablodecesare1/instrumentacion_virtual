import socket
import ipaddress
from InstVirtualLib.Sweep.GUI.network_finder.constants import PUERTO_SCPI, TIMEOUT_SCPI
import subprocess
import re
def obtener_ip_local():
    """
    Devuelve una IPv4 "real" (no loopback) en Linux.
    No depende de 'default route'.
    """
    try:
        salida = subprocess.check_output(["ip", "-o", "-4", "addr", "show", "up"], text=True)
        # Ejemplo de línea:
        # 2: enp1s0    inet 10.42.0.1/24 brd 10.42.0.255 scope global enp1s0\       valid_lft forever preferred_lft forever
        for linea in salida.splitlines():
            m = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", linea)
            if m:
                ip = m.group(1)
                if not ip.startswith("127."):
                    return ip
    except Exception:
        pass

    return "127.0.0.1"


def obtener_red_local() -> list[ipaddress.IPv4Address]:
    ip = obtener_ip_local()
    return list(ipaddress.IPv4Network(ip + "/24", strict=False).hosts())

def consultar_idn(ip: str) -> str | None:
    try:
        with socket.create_connection((ip, PUERTO_SCPI), timeout=TIMEOUT_SCPI) as s:
            s.sendall(b"*IDN?\n")
            return s.recv(1024).decode(errors="replace").strip()
    except Exception:
        return None

def enviar_scpi(ip: str, comando: str) -> str | None:
    try:
        with socket.create_connection((ip, PUERTO_SCPI), timeout=2) as s:
            s.sendall((comando + "\n").encode())
            return s.recv(4096).decode(errors="replace").strip()
    except Exception:
        return None