import glob
import pandas as pd

############################################################################
#### Burst averaging function for Sen18 data
############################################################################
def sen18_repair(pull_dir, push_dir):
    """Takes in each full Seneca 2018 table, burst averages every 15 minutes

    Args:
        pull_dir (str): directory where data is stored
        push_dir (str): directory where data is going

    """
 
    for x in glob.glob(pull_dir + "SEN18_*.csv"):
        # catch the end of the string to paste on the new file 
        y = x.rsplit('/')[-1]

        df = pd.read_csv(x)
        df['time'] = pd.to_datetime(df['time']) 
        # df = df.iloc[:-38] 

        rsmp = df.resample('15T', on ='time', label='right', closed='right', origin='start').mean()
        rsmp.to_csv(push_dir + "avgd_"+ y)

############################################################################
#### Function for checking on results of averaging
############################################################################
def comprehensh(dataframe):
    """Returns a list of comparisons between each row as a check on burst avg

    Args:
        dataframe (dataframe): Input a burst averaged dataframe
    """
    dff = dataframe['time']
    c = [dff[i] for i in range(1, len(dff)) if (dff[i] - dff[i-1]) >= (dff[2000] - dff[1999])]
    return(c)

############################################################################
#### Implement the code
############################################################################

if __name__ == '__main__':

    dir1 = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/SEN18/"
    dir2 = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/SEN18_avgd/"

    # Run the repairer function for burst averaging of Sen 2018 data
    sen18_repair(dir1, dir2)

    # check on the burst average output
    df = pd.read_csv("/home/mpoe/adcp_habs/data/adcp_tables_stacked/SEN18/SEN18_converted_time_series.csv") #, skiprows=1)
    df['time'] = pd.to_datetime(df['time'])

    # show time delta to check for correctness 
    comprehensh(df)