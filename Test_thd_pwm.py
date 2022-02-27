import sys
from time import sleep
from matplotlib import pyplot
from matplotlib.pyplot import plot, sci
from pyrsistent import v
import scipy
sys.path.insert(0, 'InstVirtualLib')
import numpy as np
from InstVirtualLib.mediciones import Mediciones

from scipy import signal,fft
import matplotlib.pyplot as plt



samples = 3000
freq = 50

t = np.linspace(0, 1, samples, endpoint=False)
pwm = signal.square(2 * np.pi * freq * t,duty = 0.6)

pyplot.magnitude_spectrum(pwm, color ='green')
plt.show()
thd = Mediciones.THD("",t,pwm,samples)
print("THD:%.2f%%"%(thd*100))


