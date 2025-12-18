import pyvisa

rm = pyvisa.ResourceManager()
inst = rm.open_resource("TCPIP::192.168.0.102::2525::INSTR")

print(inst.query("*IDN?"))  # chequeo de conexión

# IMPORTANTE: usar read_raw(), no query()
inst.write("C1:WF? ALL")  # pedir datos binarios
raw = inst.read_raw()      # leer binario crudo
print("Bytes recibidos:", len(raw))

inst.close()