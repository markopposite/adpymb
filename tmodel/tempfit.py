import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit 
# from temp_module.tempmb import TempMb as tmb

def select(adcp, flx, start, end, depth=0):
    """function to choose data to work with by lake and time interal, choose a depth to create tables of a single depth"""
    adcp['time'] = pd.to_datetime(adcp['time'])
    select_adp = adcp[(adcp['time'] > start) & (adcp['time'] < end)]

    flx['time'] = pd.to_datetime(flx['Timestamp_EST'])
    flx = flx[['time', 'Temperature_C', 'Depth_m']]
    select_flx = flx[(flx['time'] > start) & (flx['time'] < end)]

    if depth > 0:
        select_adp = select_adp[['time', str(depth)+".61"]]
        select_flx = select_flx[select_flx["Depth_m"] == depth]

    def drop(tbl,n):
        # Dropping last n rows using drop
        tbl.drop(tbl.tail(n).index, inplace = True)
        # randomly drop data to make dfs the same length 
        np.random.seed(10)
        drop_indices = np.random.choice(tbl.index, n, replace=False)
        tbl_drop = tbl.drop(drop_indices)
        return(tbl_drop.head())

    # compare the two existing sets, and make the same size through random removal of excess rows
    # TODO refactor the next block using either pd.resample(..., ) OR pd.merge_asof(..., method=nearest)

    print(len(select_adp),"adp")
    select_adp = select_adp.iloc[::3]
    print(len(select_flx), "flx", len(select_adp), "adp")

    if len(select_adp) > len(select_flx):
        n = len(select_adp) - len(select_flx)
        drop(select_adp, n)
        print("Dropped "+str(n)+" random values from sel_adp")
    else:
        n = np.abs(len(select_flx) - len(select_adp))
        drop(select_flx, n)
        print("Dropped "+str(n)+" random values from select_flx")

    print(len(select_flx), "flx", len(select_adp), "adp")
    return(select_adp, select_flx)


def model_fit(adcp, flx, start, end, depth=0):
    sel = select(adcp, flx, start, end, depth=depth)
    sel_adp, sel_flx = sel[0], sel[1]
    # the general form used is amp(temp, depth) and will be inverted in the plotting
    backscatter = sel_adp.iloc[:,1] # backscatter
    temperature = sel_flx['Temperature_C'] 

    # general form found from rearranging existing theory to find temp(amp)
    def fit(x, a, b):
        return ((x + a) * 10**(1520/(x + 273)))/b
    
    # parameter fit using the above x, y values and temp function
    popt, pcov = curve_fit(fit, temperature, backscatter)
    popt, pcov

    mb_temp = fit(temperature, popt[0], popt[1])

    plt.scatter(backscatter, temperature, marker= 'x', color='black')
    plt.scatter(mb_temp, temperature, marker = '+', color='red') # ,popt[2],popt[3]))

    plt.grid()
    plt.xlabel('Measured Backscatter (dB)')
    plt.ylabel('Temp (c)')
    plt.rcParams["figure.figsize"] = (12,8)
    plt.title('T(Measured Backscatter) Data fit')
    plt.xlim(60,75)


    # aggregating the selecet for bubble plot function
def sel_bub(adcp, flx, start, end):

    # resample and reshape the adcp dataframe
    rsmp = adcp.resample('15T', on ='time', label='right', closed='right', origin='start').mean()
    df = rsmp.reset_index([0])
    adp_melt = pd.melt(df, id_vars='time').rename(columns={'variable':'depth','value':'mb'})
    
    # ensure proper format and date range selection
    adp_melt['time'] = pd.to_datetime(adcp['time'])
    select_adp = adp_melt[(adp_melt['time'] > start) & (adp_melt['time'] < end)]

    flx['time'] = pd.to_datetime(flx['Timestamp_EST'])
    flx = flx[['time', 'Temperature_C', 'Depth_m']]
    select_flx = flx[(flx['time'] > start) & (flx['time'] < end)]

    # check that we are still working with standard dataframes
    adp_sel = pd.DataFrame(select_adp)
    flx_sel = pd.DataFrame(select_flx)

    # ensure data types and column names are similar before merge
    flx_sel[["depth"]] = flx_sel[['Depth_m']].astype(float)+0.61
    flx_sel['Temperature_C'] = flx_sel['Temperature_C'].astype(float)
    adp_sel[['depth']] = adp_sel[['depth']].astype(float)
    adp_sel['mb'] = adp_sel['mb'].astype(float)

    # sort dfs by time
    adp_sel = adp_sel.sort_values(by='time')
    flx_sel = flx_sel.sort_values(by='time')
    # drop uneeded columns
    flx_sel = flx_sel.drop(columns='Depth_m')

    # merge the two data frames, returns an empty mb column
    merged_df = adp_sel.merge(flx_sel, how='right', left_on=['time','depth','mb'], right_on=['time','depth','Temperature_C'])
    # merge the merged df with the adp df to obtain the mb values
    merged_df2 = pd.merge_asof(merged_df, adp_sel, on='time', direction='nearest', allow_exact_matches=False)
    # drop the excess columns obtained by the last merge
    merge_df = merged_df2.drop(columns=['depth_x','mb_x'])

    return(merge_df)

def bubble(ary=[], *prms):
    """Takes array as input with the following format [adcp_df, flx_df, start_time, end_time]"""
    df = sel_bub(ary[0], ary[1], ary[2], ary[3])
    time = df['time']
    temp = df['Temperature_C']
    depth = df['depth_y']
    mb = df['mb_y']

    plt.scatter(time, temp, s=depth*20, c=mb, alpha=0.2, cmap='seismic', edgecolors='black', linewidths=1)
    plt.colorbar(orientation='vertical', location='right')
    plt.grid(linestyle='-', color='grey', alpha=0.5)


if __name__ == '__main__':
    # write prompts 
    # execute the following code
    # pull the adcp tables
    lake = "OWS19"
    directory = "/home/mpoe/adcp_habs/data/adcp_tables_stacked/"
    adp = pd.read_csv(directory + "/" + lake + "/" + lake + "_mb_av.csv")
    adp_ts = pd.read_csv(directory + "/" + lake + "/" + lake + "_converted_time_series.csv")

    # choose lake, year, interval and depth
    start = "2019-07-01 12:00:00"
    end = "2019-08-02 12:00:00"
    dpth = 8 # depth in meters

    # plot
    model_fit(adp, ows, start, end, depth=dpth)

    # flx csv
    flx = pd.read_csv("/home/mpoe/adcp_habs/data/flx_data/flx_most_recent.csv").dropna()
    # site number to lake name 
    seneca, owasco, skaneateles = (flx.Site.unique()[0], flx.Site.unique()[1], flx.Site.unique()[2])
    # separate dfs by lake
    sen, ows, skn = (flx[flx["Site"] == seneca], flx[flx["Site"] == owasco], flx[flx["Site"] == skaneateles])