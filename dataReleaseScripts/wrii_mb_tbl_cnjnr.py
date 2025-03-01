import os
import glob
import numpy as np
import pandas as pd

############################################################################
#### Aggregating function to pull mb tables together for each lake-year
############################################################################

def mb_df(lake_id, year, pull_dir, push_dir):
    """
    Take in mb csv's output from wrii adn return aggregated mb table for each lake-year

    Parameters:
    ---------
    lake_id : str
        OWS19, SEN18, SKN19... ; identify the lake and the year matching raw data files
    year: str
        2018, 2019, 2020 in string format

    pull_dir: str
        directory from which data is being pulled to aggregate

    push_dir: str
        directory to which the aggregated raw tables will be stored

    Returns
    -------
    dataframe: csv
    
    """

    file_directory = pull_dir + year + '/*/'+ lake_id +'*.csv'
    pt_dir = push_dir + lake_id + '_unprocd_stacked.csv'

    # collect the tables
    df_list = [pd.read_csv(file_path, 
                       parse_dates=[[1,2,3,4,5,6,7]], 
                       header=None) for file_path in glob.
                       glob(file_directory)
                       ]
    df = pd.concat(df_list, 
                          ignore_index=False
                          )
    df.to_csv(pt_dir, 
                     index=False
                     )
    df = df.rename(columns={'0':'ens'}
                   )
    # Recreate the timestamp column from the time column-aggregate
    df["1_2_3_4_5_6_7"] = pd.to_datetime('20'+df['1_2_3_4_5_6_7'], 
                                        format="%Y %m %d %H %M %S %f", 
                                        )
    # Sort by timestamp, reset built-in index, drop extra column
    df = df.rename(columns={"1_2_3_4_5_6_7":'time'}
                   ).sort_values(by=['time']
                                 ).reset_index(
                                 ).drop(columns='index'
                                        )
    
    # for 2018 Seneca only, turn on or off when needed
    # rsmp = df.resample('15T', on ='time', label='right', closed='right', origin='start').mean()
    # return(rsmp)

    return(df)

#############################################################################
#### Function for slicing, inserting cols, renaming and restructuring tables
#############################################################################
def bld_tbl(stacked_df, num_bins, lake_id):
    """
    Takes in the stacked and labeled df, returns four tables for all beams and average backscatter
    Directory for storage is hard coded into the function

    Parameters:
    ---------
    stacked_df : dataframe
        takes a full aggregated mb dataframe as input
    num_bins: int
        number of bins for each lake: 26 (SKN), 28 (OWS), or 30 (SEN)

    lake_id: str
        OWS19, SEN18, SKN19... ; identify the lake and the year matching raw data files

    Returns
    -------
    Writes five tables per lake-year to csv in the storage directory; beams 1-4, and beam average table
    

    """

    # reconstruct list of nominal column depths
    y = [str(i) for i in np.round(np.linspace(1.61, num_bins+.61, num_bins), 2)]

    # build each table slicing df 
    bm1, bm2, bm3, bm4, avg = [stacked_df.iloc[0:, (num_bins*i + 2 ):num_bins*(i+1) +2 ] for i in range(0,5)] 
    # build each table slicing rsmp for sen18 
    # bm1, bm2, bm3, bm4, avg = [stacked_df.iloc[0:, num_bins*(i-1):num_bins*i] for i in range(1,6)] 

    # collect dfs, rename columns, insert 'time' and 'ens'
    jk, jkjk = [[bm1, bm2, bm3, bm4, avg], []]
    for i in jk:
        i.columns = y
        i.insert(0, column='time', value=df_time)
        i.insert(1, column='ens', value=df_ens)
        jkjk.append(i)

    # directory for keeping the new dfs
    direct = "/home/mpoe/adcp_habs/data/2023_mb_csv_exports/stacked_mb_tables/procd_stackd/"+lake_id+"/"

    # create the storage directory
    try:
        os.makedirs(direct, exist_ok=True)
        print("Created directory %s successfully" % direct)
    except OSError as error:
        print("Directory %s cannot be created" % direct)

    # write the tables to disk    
    for x in range(0,5):
        if x < 4: 
            jkjk[x].to_csv(direct+lake_id+"_mb_bm"+ str(x+1) +".csv", index=False)
        if x == 4:
            jkjk[4].to_csv(direct+lake_id+"_mb_avg.csv", index=False)

#############################################################################
#### Implement the code
#############################################################################
if __name__ == '__main__':

    # define dirs and lake-year
    name1 = '/home/mpoe/adcp_habs/data/2023_mb_csv_exports/'
    name2 = '/home/mpoe/adcp_habs/data/2023_mb_csv_exports/stacked_mb_tables/unprocd_stacked/'

    l = 'SEN19'
    year = '2019'
    file_directory = name1 + year + '/*/'+ l +'*.csv'
    pt_dir = name2 + l + '_unprocd_stacked.csv'

    # run the df function, set variables
    df = [mb_df(l, year, name1, name2)]
    df_time = df['time']
    df_ens = df['ens']

    # build the mb tables, input number of bins lake-year
    bld_tbl(df,30,l)
    
    check_table = pd.read_csv("/home/mpoe/adcp_habs/data/2023_mb_csv_exports/stacked_mb_tables/procd_stackd/"+ l +"/"+ l +"_mb_avg.csv")
    check_table

#############################################################################
#### block of code for sen18
#############################################################################

    # rsmp = [mb_df(l, year, name1, name2)]
    # df_time = df['time']
    # df_ens = df['ens']
    # bld_tbl(rsmp, 30, "SEN18")

    # check_table = pd.read_csv("/home/mpoe/adcp_habs/data/2023_mb_csv_exports/stacked_mb_tables/procd_stackd/"+ l +"/"+ l +"_mb_avg.csv")
    # check_table
