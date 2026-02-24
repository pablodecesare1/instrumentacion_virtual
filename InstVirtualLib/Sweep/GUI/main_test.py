from vxi11 import vxi11

from InstVirtualLib.osciloscopios import RIGOL_DS2202

if __name__ == "__main__":
    vxi11_instr = vxi11.Instrument("192.168.0.101")  # TODO: parametrizar IP
    scope = RIGOL_DS2202(handler=None, VXI11=vxi11_instr)
    idn = scope.print_ID()
    scope.close()
    print(f"EL IDN es: {idn}")