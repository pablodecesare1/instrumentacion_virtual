import pyvisa
import vxi11

from InstVirtualLib.Sweep.GUI.ui_final import App
from InstVirtualLib.instrument import Instrument
from InstVirtualLib.osciloscopios import RIGOL_DS2202

if __name__ == "__main__":
    App().mainloop()