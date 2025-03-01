##### defining constants #####

"""Constants defined in the measured backscatter sonar equation. """

# water viscosity in N*s/m2
B_W = 3.38e-6

# emitted frequency in kHz
F = 614.4
# F = 1500 # for a different adcp

# density of fresh water in kg/m3
RHO_W = 1e3

# gravitational acceleration on earth in m/s2
G = 9.81

# scale factor: to convert from neper to dB
NEPER = 8.687

# scale factor: 20,836,617,636.1328 Hz to 1 K
KELVIN = 21.9e6

# scale factor in pressure function, found in  https://pubs.usgs.gov/tm/03/c05/tm3c5.pdf
P_SCALE = 6.54e-4

# collect constants from the water absorption coefficient term
BETA = NEPER * B_W * F**2 * 1/KELVIN

# Transmit Length in meters; same size as bin for this project, documented in workhorse and winriver user guides
L_XMIT = 1

# Beam angle from the transducer head in degrees
THETA = 20

# Transducer area in m^2, this needs checked for accuracy for RDI Rio Grand/Sentinel
TRANSDUCER_AREA = .000707 

# Blanking distance for finger lakes data set
BLANK = 0.5 
