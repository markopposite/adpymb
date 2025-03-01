import glob
import pandas as pd

############################################################################
#### Function for repairing timestamp issue for Seneca 2019 data files
############################################################################
def ts_repairer(csv, ts_corr_dir):
    """Takes in dataframe and adjoins a corrected timestamp column

    Args:
        csv (dataframe): Filepath to Seneca 2019 csv
        ts_corr_dir (str): Filepath to corrected timestamp data

    Returns:
        dataframe: W/ corrected timestamp column added, written to disk
    """
    corr_ts = pd.read_csv(ts_corr_dir, skiprows=1)
    dataframe = pd.read_csv(csv)

    df = corr_ts.rename(columns={'Card time': 'time', 'Card Adj' : 'time_adj'})
    df['time'] = pd.to_datetime(df.time)
    df['time_adj'] = pd.to_datetime(df.time_adj)

    time_adj = df['time_adj']
    dataframe = dataframe.join(time_adj)

    print(dataframe.iloc[0:1,:])
    dataframe.to_csv(csv, index=False)

    return (dataframe)


############################################################################
#### Implement the code
############################################################################

# Example usage
if __name__ == "__main__":

    drctry = glob.glob("/home/mpoe/adcp_habs/data/2023_mb_csv_exports/stacked_mb_tables/procd_stackd/SEN19/*.csv")
    print([i for i in drctry])

    for i in drctry:
        ts_repairer(i)