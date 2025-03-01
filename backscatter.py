"""
Takes in ADCP raw data filepath, and outputs converted data tables
Filepath can point to many, or to solitary data files
Make sure your raw data files are in the correct .PDO or .000 format with readable id names 
Ex: for Owasco 2019 we might use OWS19000.000, OWS19001.PDO etc...
"""

import os
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import rpy2.robjects as robjects

from temp_module import tempmb
from temp_module.constants import *
from tables.subsetter import subset_adcp
from tables.conjoiner import aggr_df
from tables.converter import tec, mb_build

######################################################################################
def chg_str(fl):
    """takes a filename found using the given lake id
    Separates the file formatting and keeps an id per filename"""

    x = fl.rsplit('/')
    y = x[-1].rsplit('.') 
    z = y[0].rsplit('r')

    lake_id = z[0]
    print(lake_id)
    return(lake_id)

######################################################################################

def auto_mb(raw_dir, end_dir, eyedee):
    """
    Takes the three input params and spits out the final converted data tables for each beam 
    Convention: include a trailing slash '/ at the end of any filepath name
    """

    direct1 = end_dir +"adcp_data_tables/"
    direct2 = end_dir+"adcp_tables_stacked/"
    print(raw_dir, direct1, direct2)

    try:
        os.makedirs(direct1, exist_ok =True)
    except OSError as error:
        print(error)
    try:
        os.makedirs(direct2, exist_ok =True)
    except OSError as error:
        print(error)

    for file in glob.glob(raw_dir+"*/*"+eyedee+"*"):
        print(file)
        laek_eyedee = chg_str(file)
        print(laek_eyedee)

        ######################################################################################
        # subsetter
        # ex: csv_dir = "/home/mpoe/adcp_habs/data/adcp_data_tables/SEN19000"
        csv_dir = direct1+laek_eyedee+"/"
        try:
            os.makedirs(csv_dir, exist_ok=True)
        except OSError as error:
            print(error)

        print("now on to subset")

        subset_adcp(file, laek_eyedee, csv_dir) # module py2 not working in all environments
    ######################################################################################
    # conjoiner 
    # array for looping through all of the categories and build all tables in one go
    categories = ["amp_avg", "amp_beam1", "amp_beam2", "amp_beam3", "amp_beam4", "corr_bm1", "corr_bm2", "corr_bm3", "corr_bm4", 
                "prcnt_good_bm1", "prcnt_good_bm2", "prcnt_good_bm3", "prcnt_good_bm4", "table_time_series", "vel_E_W", 
                "vel_err", "vel_N_S", "vel_x_vrt", ]
    
    # a single lake-year: tables for all categories
    for i in categories: 
        tester = aggr_df(eyedee, i, direct1, direct2)
    # bins table 
    aggr_df(eyedee, "table_bins", direct1, direct2, sort_key="bin_depth")

    ######################################################################################
    # ts table builder
    # filepath = "/home/mpoe/adcp_habs/data/adcp_data_tables/OWS19002/OWS19002_" 
    # filepath = final_dir + adp_id + "/" + adp_id + "_" # file path
    filepath = direct2+ adp_id + "/" + adp_id + "_" 

    ######################################################################################
    # time series conversion build
    temp_check = pd.read_csv(filepath + "table_time_series.csv")
    pnt_dir1 = filepath + "converted_time_series.csv"
    test_ts = tec(temp_check, pnt_dir1) # works without explicit function call, the table write is built in

    ######################################################################################
    # mb table builder
    # pull time series and amplitude tables 
    cats = ['beam1', 'beam2', 'beam3', 'beam4', 'avg']
    #generate mb tables 
    for i in cats:
        amp_check = pd.read_csv(filepath + "amp_" + i + ".csv") 
        pnt_dir_mb = filepath + "mb_" + i + ".csv"
        test_df = mb_build(amp_check, temp_check, pnt_dir_mb)
        # print(len(test_df), '\n' , test_df.iloc[10000, :])


if __name__ == '__main__':
    # ex: df_adcp = "/home/mpoe/adcp_habs/data/RawDataClean/"
    df_adcp = input("Enter raw data filepath path. Example: ~/user/data/raw_data/")
    # ex: /home/mpoe/adcp_habs/data/
    final_dir = input("Enter storage filepath path. Example: ~/user/data/")
    # ex: adp_id = 'SEN19280' 
    adp_id = input("Please enter an experiment ID. Example: 'SEN19' will work for all Seneca 2019 adcp files named SEN1900x...")
    auto_mb(df_adcp, final_dir, adp_id)

        