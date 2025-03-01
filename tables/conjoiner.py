""" Takes in data tables for adcp measurements and creates large aggregated tables for each parameter

"""

import pandas as pd
from pathlib import Path
import glob

def aggr_df(lake_id, category, dir1, dir2, sort_key="time", pth=False): 
    """ Takes in csv's for a lake and category and returns a stacked table
     
    Parameters
    ---------
    lake_id : str
        OWS19, SEN18, SKN19... ; identify the lake and the year matching raw data files
    category : str
        amp_av, vel_N_W, corr_bm_1...; many categories exist for each raw data file
    dir1 : str
        directory where the separated data tables are located
    dir2 : str
        directory where the stacked data tables will end up
    format examples: 
        dir1 = "adcp_habs/data/adcp_data_tables/"
        dir2 = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/"
    sort_key : str
        default sorting by time
    pth : boolean
        set to True for use with Denali or if trouble with remote server


    Returns
    -------
    csv
        one large table written to a new file and read back in
    """
    
    # directory business
    file_directory = dir1 + lake_id + "*/*" + category + "*.csv"
    pt_dir = dir2 + lake_id
    pt_file = pt_dir + "/" + lake_id + "_" + category + ".csv"
    # define in pathlib format and write the directory if not exist
    point_directory = Path.home()/Path(pt_dir)
    point_directory.mkdir(parents=True, exist_ok=True)

    # pull the files and create list of df's
    df_list = []
    if pth:
        for file_path in Path.home().glob(file_directory):
            indiv_csv = pd.read_csv(file_path)
            df_list.append(indiv_csv)
    else:
        for file_path in glob.glob(file_directory):
            indiv_csv = pd.read_csv(file_path)
            df_list.append(indiv_csv)

    # change all dfs in list to have matching column names
    cols = df_list[0].columns
    for i in df_list:
        i.columns = cols

    # stack df's into one table and sort by time
    concat_df = pd.concat(df_list, ignore_index=True)
    concat_df = concat_df.sort_values(sort_key, ascending=True) 

    # write df as csv to disk and read back in
    concat_df.to_csv(pt_file, index=False)
    csv_read = pd.read_csv(pt_file)

    return (csv_read)

################################################################################################
if __name__ =='__main__':
    # run prompts asking for directory and file info
    # then execute functions
    

    # general directory structure; 
    name1 = "adcp_habs/data/adcp_data_tables/"
    name2 = "/home/mpoe/adcp_habs/repos/test_dir/test_data2/"

    # array for looping through all of the categories and build all tables in one go;
    # recommended: only run one lake*year at a time for categories list
    categories = ["amp_avg", "amp_beam1", "amp_beam2", "amp_beam3", "amp_beam4", "corr_bm1", "corr_bm2", "corr_bm3", "corr_bm4", 
                "prcnt_good_bm1", "prcnt_good_bm2", "prcnt_good_bm3", "prcnt_good_bm4", "table_time_series", "vel_E_W", 
                "vel_err", "vel_N_S", "vel_x_vrt", ]


    # a single lake*year: tables for all categories
    laek_idee = "OWS19"
    for i in categories: 
        tester = aggr_df(laek_idee, i, name1, name2, pth=True)

    aggr_df(laek_idee, "table_bins", name1, name2, sort_key="bin_depth")

    pass


