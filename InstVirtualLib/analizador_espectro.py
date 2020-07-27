"""
Created on Fri Oct 26 10:07:15 2018

@author: Federico Bua, Lucas Manfredi

"""

from instrument import Instrument
import numpy as np
from struct import unpack

#------------------------------------------------------------------------------
#------------------------- BASE CLASS -----------------------------------------
#------------------------------------------------------------------------------


class analizador_espectro(Instrument):
	
	def __init__(self,handler):
		super().__init__(handler)

	def set_freq_center(self,Hz):
		pass
	def set_freq_start(self,Hz):
		pass
	def set_freq_stop(self,Hz):
		pass
	def set_span(self,Hz):
		pass

	def set_referencelevel(self,dBm):
		pass
	def set_atenuator(self,dB):
		pass

	def set_RBW(self,Hz):
		pass
	def set_VBW(self,Hz):
		pass
	def set_sweeptime(self,s):
		pass

	def get_marker(self): #retornar frecuencia y amplitud
		pass
	def peaksearch(self):
		pass
	def set_marker_delta(self,marker):
		pass
	def set_marker_freq(marker,self,Hz):
		pass

	def get_trace(self):
		pass

#------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------Analizador de espectro DSA815---------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------
class Rigol_DSA800(analizador_espectro):
	def __init__(self,handler):
		super().__init__(handler)
		
	def set_freq_center(self,Hz):
		self.write(":SENSe:FREQuency:CENTer "+str(Hz))

	def set_freq_start(self,Hz):
		self.write(":SENSe:FREQuency:STARt "+str(Hz))

	def set_freq_stop(self,Hz):
		self.write(":SENSe:FREQuency:STOP "+str(Hz))

	def set_span(self, Hz):
		self.write(":SENSe:FREQuency:SPAN "+str(Hz))

	def set_referencelevel(self,dBm):
		self.write(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel "+str(dBm))

	def set_atenuator(self,dB):
		self.write(":SENSe:POWer:RF:ATTenuation "+str(dB))

	def set_RBW(self,Hz):
		self.write(":SENSe:BANDwidth:RESolution "+str(Hz))

	def set_VBW(self,Hz):
		self.write(":SENSe:BANDwidth:VIDeo "+str(Hz))

	def set_sweeptime(self,s):
		self.write(":SENSe:SWEep:TIME "+str(s))

	def get_marker(self,marker):
		a=self.query("CALCulate:MARKer"+str(marker)+":Y?")
		b=self.query("CALCulate:MARKer"+str(marker)+":X?")
		return a,b

	def peaksearch(self, marker):
		self.write(":CALCulate:MARKer"+str(marker)+":STATe ON") #MARKer1 2,3 o 4
		self.write(":CALCulate:MARKer"+str(marker)+"MAXImum:MAX")

	def set_marker_freq(self,marker,Hz):
		self.write(":CALCulate:MARKer"+str(marker)+":STATe ON") #MARKer1 2,3 o 4
		self.write(":CALCulate:MARKer"+str(marker)+":X "+str(Hz))

	def get_trace(self):
		a=self.query(":TRACe:DATA? TRACE1")
		a=a[11:-1] #Recorto el #9000009014 delantero y el \n del final
		a=np.array(a.split(", "),dtype=np.float32) #Lo separo de las comas y lo preparo para graficar
		return a


	def set_marker_delta(self,marker):
		self.write(":CALCulate:MARKer"+str(marker)+":STATe ON") #MARKer1 2,3 o 4
		self.write(":CALCulate:MARKer"+str(marker)+":MODE DELT") #Mode: POS, DELT, BAND or SPAN
		#self.write(":CALCulate:MARKer"+str(marker)+":DELTa:SET:CENTer")

	def set_marker_reference_level(self,marker):
		self.write(":CALCulate:MARKer"+str(marker)+":STATe ON") #MARKer1 2,3 o 4
		self.write(":CALCulate:MARKer"+str(marker)+":SET:RLEVel")