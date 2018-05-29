# -*- coding: utf-8 -*-
"""
Created on Fri May 11 20:05:13 2018

@author: Administrador
"""

import inspect
from instruments.instrument import Instrument


class SpectrumAnalyzer(Instrument):
    '''
        Clase generica que representa a cualquier analizador de espectro
    '''

    COMMAND_SET_AMP_UNIT = "{}"

    COMMAND_SET_RBW = ""
    COMMAND_GET_RBW = ""
    COMMAND_SET_SPAN = ""
    COMMAND_GET_SPAN = ""
    COMMAND_SET_CENTER_FREQ = ""
    COMMAND_GET_CENTER_FREQ = ""
    COMMAND_SET_SWEEP_TIME = ""
    COMMAND_GET_SWEEP_TIME = ""
    COMMAND_SET_VBW = ""
    COMMAND_GET_VBW = ""
    COMMAND_SET_REF_LEVEL = ""
    COMMAND_GET_REF_LEVEL = ""
    COMMAND_ZERO_SPAN = ""
    COMMAND_TITLE = ""
    COMMAND_SET_ATT = ""
    COMMAND_GET_ATT = ""
    COMMAND_TAKE_SWEEP = ""
    COMMAND_SINGLE_SWEEP = ""
    COMMAND_PEAK_SEARCH = ""
    COMMAND_NEXT_PEAK = ""
    COMMAND_NEXT_PEAK_RIGHT = ""
    COMMAND_NEXT_PEAK_LEFT = ""
    COMMAND_GET_MARKER_AMPLITUDE = ""
    COMMAND_GET_MARKER_FREQ = ""
    COMMAND_SET_DET_POSITIVE = ""
    COMMAND_SET_DET_QPEAK = ""
    COMMAND_SET_DET_AVERAGE = ""
    COMMAND_SET_DET_RMS = ""
    COMMAND_SET_DET_SAMPLE = ""
    COMMAND_SET_DET_NEGATIVE = ""
    COMMAND_GET_DET_TYPE = ""
    COMMAND_SET_LOG_SCALE = ""
    COMMAND_GET_LOG_SCALE = ""
    COMMAND_SET_START_FREQ = ""
    COMMAND_SET_STOP_FREQ = ""
    COMMAND_SET_RBW_AUTO = ""
    COMMAND_SET_VBW_AUTO = ""
    COMMAND_SET_SWEEP_AUTO = ""
    COMMAND_SET_CENTER_FREQ_MARKER = ""

    def __init__(self, instrument_handle):
        '''
        Doc
        '''
        super().__init__(instrument_handle)


# ============================================================================
# ============================================================================

    def setAttenuation(self, value):
        """ Set attenuation with 'value' between 0 - 70 dB's """

        self.write(self.COMMAND_SET_ATT.format(value))

    def getAttenuation(self):
        """ Return attenuation value between 0 - 70 dB's """

        return self.query(self.COMMAND_GET_ATT)

    def setRbw(self, value):
        """ Set resolution bandwith with 'value' in Hz """

        self.write(self.COMMAND_SET_RBW.format(value))

    def getRbw(self):
        """ Return resolution bandwith in HZ """

        return self.query(self.COMMAND_GET_RBW)

    def setSpan(self, value):
        """ Set span with 'value' in Hz """

        self.write(self.COMMAND_SET_SPAN.format(value))

    def getSpan(self):
        """ Return span in HZ """

        return self.query(self.COMMAND_GET_SPAN)

    def setCenterFreq(self, value):
        """ Set the center frequency with 'value' in Hz """

        self.write(self.COMMAND_SET_CENTER_FREQ.format(value))

    def getCenterFreq(self):
        """ Return the center frequency in HZ """

        return self.query(self.COMMAND_GET_CENTER_FREQ)

    def setSweepTime(self, value):
        """ Set the sweep time with 'value' in ms """

        self.write(self.COMMAND_SET_SWEEP_TIME.format(value))

    def getSweepTime(self):
        """ Return sweep_time in HZ """

        return self.query(self.COMMAND_GET_SWEEP_TIME)

    def setZeroSpan(self):
        """ Set the spectrum analyzer in zero span mode """

        self.write(self.COMMAND_ZERO_SPAN)

    def getVbw(self):

        return self.query(self.COMMAND_GET_VBW)

    def setVbw(self, value):

        self.write(self.COMMAND_SET_VBW.format(value))

    def setRefLevel(self, value):
        """ Set the reference level with 'value' in dbm """

        self.write(self.COMMAND_SET_REF_LEVEL.format(value))

    def getRefLevel(self):
        """ Return reference level in dbm """

        return self.query(self.COMMAND_GET_REF_LEVEL)

    def writeTitle(self, title):
        """ Write a title on display of spectrum analyzer """

        self.write(self.COMMAND_TITLE.format(title))

    def takeSweep(self):
        """
        Starts and completes one full sweep before the next cmd is executed.
        """
        self.write(self.COMMAND_TAKE_SWEEP)

    def preset(self):
        """
        Performs an instrument preset.
        """
        self.write(self.COMMAND_PRESET)

    def setSingleSweep(self):
        """
        Sets the spectrum analyzer to single-sweep mode.
        Each time TS (take sweep) is sent, one sweep is initiated, as long as
        the trigger and data entry conditions are met.
        """
        self.write(self.COMMAND_SINGLE_SWEEP)

    def peakSearch(self):
        """
        """
        self.write(self.COMMAND_PEAK_SEARCH)

    def nextPeak(self):
        """ {doc_method} """

        self.write(self.COMMAND_NEXT_PEAK)

    def nextPeakRight(self):
        """ {doc_method} """

        self.write(self.COMMAND_NEXT_PEAK_RIGHT)

    def nextPeakLeft(self):
        """ {doc_method} """

        self.write(self.COMMAND_NEXT_PEAK_LEFT)

    def getMkrAmplitude(self):
        """ Specifies the amplitude of the active marker in the current
        amplitude units when marker type is of fixed or amplitude type. When
        queried, MKA returns the marker amplitude independent of marker type
        """
        return float(self.query(self.COMMAND_GET_MARKER_AMPLITUDE))

    def getMkrFrequency(self):

        return self.query(self.COMMAND_GET_MARKER_FREQ)

    def setDetectorPos(self):
        """ The DET command selects the type of spectrum analyzer detection
        (positive-peak) """

        self.write(self.COMMAND_SET_DET_POSITIVE)

    def setDetectorSample(self):
        """ The DET command selects the type of spectrum analyzer detection
        (sample) """

        self.write(self.COMMAND_SET_DET_SAMPLE)

    def setDetectorQuasi(self):
        """ The DET command selects the type of spectrum analyzer detection
        (quasi peak) """

        self.write(self.COMMAND_SET_DET_QPEAK)

    def setDetectorAverage(self):
        """ The DET command selects the type of spectrum analyzer detection
        (AVERAGE) """

        self.write(self.COMMAND_SET_DET_AVERAGE)

    def setDetectorRms(self):
        """ The DET command selects the type of spectrum analyzer detection
        (sample) """

        self.write(self.COMMAND_SET_DET_RMS)

    def setDetectorNeg(self):
        """ The DET command selects the type of spectrum analyzer detection
        (negative-peak)  """

        self.write(self.COMMAND_SET_DET_NEGATIVE)

    def getDetector(self):
        """ When used as a predefined variable, DET returns a number. The
        number that is returned corresponds to the DET parameter as shown
        in the following table:
                                SMP    0
                                POS    1
                                NEG    49
        """
        return self.query(self.COMMAND_GET_DET_TYPE)

    def setLogScale(self, scale):

        self.write(self.COMMAND_SET_LOG_SCALE.format(scale))

    def getLogScale(self):

        return self.query(self.COMMAND_GET_LOG_SCALE)

    def setStartFreq(self, freq):

        self.write(self.COMMAND_SET_START_FREQ.format(freq))

    def setStopFreq(self, freq):

        self.write(self.COMMAND_SET_STOP_FREQ.format(freq))

    def setRbwAuto(self):

        self.write(self.COMMAND_SET_RBW_AUTO)

    def setVbwAuto(self):

        self.write(self.COMMAND_SET_VBW_AUTO)

    def setSwAuto(self):

        self.write(self.COMMAND_SET_SWEEP_AUTO)

    def setCenterFreqMk(self):

        self.write(self.COMMAND_SET_CENTER_FREQ_MARKER)

    def setAmplitudeUnit(self, unit):

        self.write(self.COMMAND_SET_AMP_UNIT.format(unit))

