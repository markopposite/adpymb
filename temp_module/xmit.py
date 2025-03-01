import numpy as np
from . constants import *

class Xmit():
    """Provide converted values for transmitted power, voltage, and current
    Reference power is 1 Watt

    Class attributes
    ----------------
    cts_to_amps, cts_to_volts: conversion factors from counts to amps, volts

    Instance attributes
    -------------------
    x_i: transmit current in counts 
    x_v: transmit voltage in counts

    Instance methods
    ----------
    xi: trasmit current in amps
    xv: transmit voltage in volts
    xmit_power: Find transmit power using transmission properties current and voltage in dBW
    absolute: Find absolute power from transmission
    To convert to DBm: DBm = dBW + 30
    """

    cts_to_amps = (11451/1000000)
    cts_to_volts = (380667/1000000)

    def __init__(self, x_i, x_v): 
        self.x_i = x_i
        self.x_v = x_v

    def xi(self):
        return(self.x_i * Xmit.cts_to_amps)

    def xv(self):
        return(self.x_v * Xmit.cts_to_volts)
    
    def xmit_power(self):
        y1 = self.xi()
        x1 = self.xv()
        return(10*np.log10((y1*x1)/1))
    
    def absolute(self):
        return(1 * 10**(self.xmit_power() / 10))