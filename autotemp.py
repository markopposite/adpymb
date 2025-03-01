"""generate temperature model and plots"""


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit 

from tmodel.tempfit import model_fit


######################################################################################
# t model fit 
#TODO possible prompt "continue?" b/c this is a nuanced investigation, maybe don't include the model here
# pull the adcp tables
lake = "OWS19"
directory = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/"
adp = pd.read_csv(directory + "/" + lake + "/" + lake + "_mb_av.csv")
adp_ts = pd.read_csv(directory + "/" + lake + "/" + lake + "_converted_time_series.csv")

# flx csv
flx = pd.read_csv("/home/mpoe/adcp_habs/data/flx_data/flx_most_recent.csv").dropna()
# site number to lake name 
seneca, owasco, skaneateles = (flx.Site.unique()[0], flx.Site.unique()[1], flx.Site.unique()[2])
# separate dfs by lake
sen, ows, skn = (flx[flx["Site"] == seneca], flx[flx["Site"] == owasco], flx[flx["Site"] == skaneateles])

# choose lake, year, interval and depth
# TODO maybe include all time for each model for full auto script
# TODO or include only a small selected period and run the t model script
start = "2019-07-01 12:00:00" # start[0]
end = "2019-08-02 12:00:00" # end[-1]
dpth = 8 # depth in meters

# plot
model_fit(adp, ows, start, end, depth=dpth)

