import os
import glob
import numpy as np
import pandas as pd

############################################################################
#### Function for adding ensemble #'s to files that are missing that info
############################################################################

def add_ens(pull_dir, push_dir, mb_direct, sen19=False):
    """Adds correct ensemble numbers to files that are missing them

    Args:
        pull_dir (str): _description_
        push_dir (str): _description_
        sen19 (bool, optional): for Seneca 2019 column rearrange. Defaults to False.
    """
    mb_table = pd.read_csv(mb_direct +  "_mb_avg.csv")
    ens_keep = mb_table.iloc[:,0:2]

    for i in glob.glob(pull_dir + "*.csv"):
        if "bins" in i or "Corrected" in i or "table_time_series" in i or "mb" in i or "avgd" in i:
            pass
        else:
            name = i.rsplit('/')[-1]
            g = pd.read_csv(i)
            g.insert(1, column='ens', value = ens_keep['ens'])

            if sen19:
                temp_cols = g.columns.to_list()
                new_cols = temp_cols[-1:] + temp_cols[0:-1]
                g = g[new_cols]

            # write to disk
            g.to_csv(push_dir + name, index=False)

############################################################################
#### Optional directory creation function for storage
############################################################################
def dr_create(yn=False):
    """Creates directories for final stage files for Data release

    Args:
        yn (bool, optional): Set to True to run. Defaults to False.
    """
    if yn:
        # for building table, loop through all lake*years okay for one category
        layk_idees = ["OWS19", "OWS20", "SEN18", "SEN19", "SKN19", "SEN20"]

        # create the nec. directories
        exp_dir = "/home/mpoe/adcp_habs/data/Export_Data_Release/"
        for i in layk_idees:
            print(exp_dir + i)
            try:
                os.makedirs(exp_dir + i + "/", exist_ok=True)
                print("Created directory %s successfully" % i)
            except OSError as error:
                print("Directory %s cannot be created" % i)

############################################################################
#### Implement the code
############################################################################

if __name__ == "__main__":

    yr = "2019"
    lkyr = "SEN19"

    mb_drct = "/home/mpoe/adcp_habs/data/2023_mb_csv_exports/stacked_mb_tables/procd_stackd/"+ lkyr + "/" + lkyr
    file2ens = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/"
    storage_path = "/home/mpoe/adcp_habs/data/Export_Data_Release/"

    dr_create(yn=False)

    add_ens(file2ens, storage_path, mb_drct, sen19=True)

