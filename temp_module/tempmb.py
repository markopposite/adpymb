import numpy as np
from .constants import *
"""Return properties and parameters for sonar and backscatter theory.

Classes
-------
Sonar: Return various properties of a physical freshwater system
Xmit: Return transmission and absolute power given current and voltage; convert xi and xv
TempMb: Calculate measured backscatter and 
"""

class Sonar():
    """Define fundamental physics of sonar theory for use with backscatter"""

    def __init__(self, cell_depth, temperature):
        self.cell_depth = cell_depth 
        self.temperature = temperature

    @property
    def cosine_theta(self):
        """Cosine of the beam angle from the transducer
        """
        angle = np.deg2rad(THETA)
        return(np.cos(angle))

    def pressure(self):
        """Underwater pressure
            # calculated in pascals, then converted to atmospheres 
            # see documentation: https://pubs.usgs.gov/tm/03/c05/tm3c5.pdf
        """
        h = self.cell_depth
        P = RHO_W * G * h
        return (1 - (P_SCALE * P * 0.00000987)) 
    
    def spd(self):
        """Calculate sound speed with temperature as input; ignores salinity
        """
        t = self.temperature
        c = (1.402385e3 + (5.038813)*t - (5.799136e-2)*t**2 +
                (3.287156e-4)*t**3 - 1.398845e-6* t**4 + 
                (2.787860e-9)* t**5) 
        return (c)    
    
    def r_slant(self): 
        """R(r(D, theta), Lxmit) dependent on slant distance from transducer to middle of bin
        """
        return ((self.cell_depth + (0.5 * L_XMIT)) / self.cosine_theta)  # WRII documentation
    
        # return (self.cell_depth/self.cosine_theta) # slant distance
        # return (((self.cell_depth/self.cosine_theta) + 0.5*1)/self.cosine_theta) # alternate interpretation of r from WR documentation
        # return (((0.5 + (self.cell_depth -1) + 0.5)/self.cosine_theta)) # usgs Landers et al 2016
        # return (((self.cell_depth/self.cosine_theta) + 1/4)) # usgs Wall et al pp 5, 2006
    
    def rayleigh_distance(self):
        """ Rayleigh distance for near field term psi
            Transducer area [m^2], 
            Speed of sound in water [m/s], 
            Acoustic frequency [kHz]
        """
        sound_speed = self.spd()
        wavelength = sound_speed/F
        return (TRANSDUCER_AREA/wavelength)

    def psi(self):
        """Near-Field Correction coefficient
            takes slant distance and rayleigh distance as input
        """
        r_n = self.rayleigh_distance()
        r = self.r_slant()
        x = (1.35*r)/r_n
        y = (2.5*r)/r_n
        return (1 + 1/(x + y**(3.2)))

    def f_t(self):
        """Relaxation frequency
        """
        exponent = (-1) * (1520)/(self.temperature + 273)
        return (KELVIN * 10**(exponent))

    def alpha_w(self):
        """ Water absorption coefficient
        """
        alfa = NEPER * B_W * F**2 * 1/(self.f_t())
        presher = (1 - P_SCALE * self.pressure())
        return (alfa * presher) 
    
    # def alpha_s(self):
    #     """Sediment absorption coefficient"""
    #     r = self.r_slant()
    #     w = self.alpha_w()
    #     nl = np.log(10)
    #     return ((10/(r * nl)) + w) # not working

    
class TempMb(Sonar):
    """Inherit Sonar class to calculate measured backscatter and eventually temperature"""
    def __init__(self, cell_depth, amp, t_c, t_att, t_amb,):
        super().__init__(cell_depth, t_c)
        self.amp = amp
        self.cell_depth = cell_depth 
        self.t_c = t_c
        self.t_att = t_att
        self.t_amb = t_amb

    def attitude_temp(self):
        """Calculate temp of electronics using a proportional function"""
        te = (self.temperature / self.t_amb) * self.t_att
        return (te)

    def c_amp_scale(self):
        """ Echo intensity scale
            T_e = temperature of electronics, calculated; attitude temp in OCE
            At ambient Temp; 0.43db/Count is nominal scale --> T_e = 23.0465 [c]
        """
        T_e = self.attitude_temp()
        return (127.3/(T_e + 273))
    
    def source_level(self): 
        return(self.c_amp_scale() * self.amp)
        # return(self.amp * 0.43)

    def beam_spreading(self):
        return(20 * np.log10(self.r_slant() * self.psi()))

    def water_absorption(self):
        return(2 * self.alpha_w() * self.r_slant())
    
    # def sediment_absorption(self): #incorrect
    #     return(2 * self.alpha_s() * self.r_slant())
    
    def correction(self):
        return(10 * np.log10(L_XMIT/self.cosine_theta))

    def measured_backscatter(self):
        """ Measured backscatter using definitions from teledyne winriver user guide documentation
        """
        S_l =  self.source_level()
        B_s = self.beam_spreading()
        W_a = self.water_absorption() 
        # alpha = self.water_absorption() + self.alpha_s()
        correction = self.correction()
        return (S_l + B_s + W_a - correction)

    def _temp_mb(self):
        """ Function of Temperature wrt amplitude and cell depth; Includes the pressure corrections
        returns invalid values within the log functions. Could potentially be exapanded, but is best modelled empirically
        """
        M_B, S_L, R = (self.measured_backscatter(), self.source_level(), self.r_slant())
        P, log_r = (self.pressure(), np.log10(R)) 
        
        b1, delta_l = ((10*log_r), np.abs((S_L-M_B)/4))
        a, b = (np.log10(delta_l-b1), np.log10(R* BETA* P))
        if RuntimeError:
            raise AttributeError("Function is divergent, seek empirical model")
        return ((1520/(a-b)) - 273)
    
    def offset(self):
        """Calculate the offset that the workhorse documentation uses in their temp function
            We have the conversion from T_amb to T_c
        """
        x, a0, a1, a2, a3 = (self.t_amb, 9.82697464E1, -5.86074151382E-3, 1.60433886495E-7, -2.32924716883E-12 )
        y = self.t_c - (((a3*x + a2)*x + a1)*x + a0)
        return(y)

    def _temperature_workhorse(self, offst=-87):
        """ From adcp workhorse documentation, 
            Takes temperature data in rssi cts to convert to celcius
        """
        # offset = self.offset() # be careful of circular usage
        off_set = offst
        x, a0, a1, a2, a3 = (self.t_att, 9.82697464E1, -5.86074151382E-3, 1.60433886495E-7, -2.32924716883E-12)
        return (off_set + ((a3*x + a2)*x + a1)*x + a0)


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