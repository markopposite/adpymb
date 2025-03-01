""" Converts time series raw data into ascii and generates backscatter tables """

import os 
import pandas as pd
import glob

from temp_module import tempmb
from temp_module.constants import *


# Time series converted table build
def tec(df1, pt_dir):
    """Takes time series table and array of amplitude tables to convert to backscatter tables"""
    t, tamb, tatt, xii, xvv = (df1["temp"], df1["ambient_T"], df1["attitude_T"], df1["xmit_i"], df1["xmit_v"])

    tmb = tempmb.TempMb(0, 0, t, tatt, tamb)
    x = tmb.c_amp_scale()
    y = tmb.attitude_temp()

    xmb = tempmb.Xmit(xii, xvv)
    xcurr = xmb.xi()
    xvolt = xmb.xv()

    df_bld_dict = {"Amp_scl_fctr": x, "electr_T": y, "xmit_current": xcurr, "xmit_voltage":xvolt}
    dat1 = pd.DataFrame(df_bld_dict)
    dat2 = df1.join(dat1)

    dat2.to_csv(pt_dir, index=False) 
    g = pd.read_csv(pt_dir)
    return(g)


# function version for mb build
def mb_build(amp_table, df_ts, pt_dir):
    """Takes time series table and array of amplitude tables to convert to backscatter tables"""
    tmp, tamb, tatt = (df_ts["temp"], df_ts["ambient_T"], df_ts["attitude_T"])

    # loop over amp df and separate each column into series
    df_mb = []
    df_mb.append(amp_table['time'])

    for x in amp_table:
        """Build mb table by operating mb function column by column"""
        # loop over string-type depths, ignoring time
        if x.startswith('time'):
            pass
        else:
            dep = float(x)
            # function to input only amplitude series by depth
            def tp_mb(y):
                tm = tempmb.TempMb(dep, y, tmp, tatt, tamb).measured_backscatter()
                return (tm)
            
            # set column as series for processing
            amp_x = amp_table[x]
            # run the function on the series
            mb_series_x = tp_mb(amp_x)
            # set new series as dataframe component with corresponding headings
            mb_df_x = pd.Series(mb_series_x, name=x)
            # add processed mb series to a list
            df_mb.append(mb_df_x)

    # Build and return mb table 
    df = pd.concat(df_mb, axis=1)

    # apply WR near zone corrections; TODO verify explicitly before using
    # df.iloc[:,1] += 1
    # df.iloc[:,2] += 0.5

    # save tp csv
    df.to_csv(pt_dir, index=False) 
    # read csv back in for fun
    g = pd.read_csv(pt_dir)
    return (g)


################################################################################################

if __name__ == '__main__':
    # gather necessary info
    ident = input("Enter lake year is i.e. SEN19... ")
    # dir_input = input("Enter data directory to pull from... ")
    directory = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/" + ident + "/" + ident + "_"

    # time series conversion
    temp_check = pd.read_csv(directory + "table_time_series.csv")
    pnt_dir1 = directory + "converted_time_series.csv"
    test_ts = tec(temp_check, pnt_dir1)

    # backscatter calculations and table builds
    cats = ['beam1', 'beam2', 'beam3', 'beam4', 'avg'] 
    for i in cats:
        amp_check = pd.read_csv(directory + "amp_" + i + ".csv") 
        pnt_dir_mb = directory + "mb_" + i + ".csv"
        test_df = mb_build(amp_check, temp_check, pnt_dir_mb)
        # print(len(test_df), '\n' , test_df.iloc[10000, :])

    