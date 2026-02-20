import socket
import ipaddress
from InstVirtualLib.Sweep.GUI.network_finder.constants import PUERTO_SCPI, TIMEOUT_SCPI

def obtener_ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

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