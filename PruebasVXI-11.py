import matplotlib.pyplot as plt
import numpy as np
import vxi11


def read_data(inst_ip, chann, timeout=10000):
    # --- CONEXIÓN ---
    scope = vxi11.Instrument(inst_ip)
    scope.timeout = timeout  # ms

    # --- CONFIGURACIÓN DE CAPTURA ---
    scope.write(f":WAV:SOUR {chann}")
    scope.write(":WAV:MODE RAW")  # leer todos los puntos
    scope.write(":WAV:FORM BYTE")  # formato binario

    # --- LECTURA DEL PREÁMBULO (ESCALAS) ---
    preamble = scope.ask(":WAV:PRE?").split(",")
    # índices según Rigol:
    # [0]FORMAT,[1]TYPE,[2]POINTS,[3]COUNT,[4]xincr,[5]xorig,[6]XREF,[7]yincr,[8]yorig,[9]yref
    xincr = float(preamble[4])
    xorig = float(preamble[5])
    yincr = float(preamble[7])
    yorig = float(preamble[8])
    yref = float(preamble[9])

    # --- LECTURA DE DATOS BINARIOS ---
    scope.write(":WAV:DATA?")
    raw = scope.read_raw()

    # --- DECODIFICAR BLOQUE BINARIO #9xxxx... ---
    if raw.startswith(b"#"):
        num_digits = int(raw[1:2].decode())
        num_bytes = int(raw[2 : 2 + num_digits].decode())
        data = raw[2 + num_digits : 2 + num_digits + num_bytes]
    else:
        raise ValueError("Bloque binario inválido o encabezado no detectado")

    # --- CONVERTIR DATOS ---
    y_raw = np.frombuffer(data, dtype=np.uint8)
    y = (y_raw - yref) * yincr + yorig
    x = np.linspace(0, (len(y) - 1) * xincr, len(y)) + xorig

    scope.close()

    return (x, y)


if __name__ == "__main__":
    # --- CONFIGURACIÓN ---
    inst_ip = "10.42.0.47"  # reemplazá por la inst_ip real del osciloscopio
    CHANNEL = "CHAN2"

    X, y = read_data(inst_ip, CHANNEL)

    # --- PLOTEO ---
    plt.figure(figsize=(10, 5))
    plt.plot(X, y)
    plt.title(f"Rigol DS2202 - {CHANNEL}")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Voltaje [V]")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
