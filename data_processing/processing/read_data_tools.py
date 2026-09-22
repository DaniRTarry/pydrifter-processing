"""
author: @SebEssink
        email: sessink@mit.edu
        @Tarry
        email: drtarry@imedea.uib-csic.es

type: FUNCTION

description: set of tools used to read drifter data

"""

# Load libraries
import math
import numpy as np
import pandas as pd
import xarray as xr


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371*1e3
    
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    
    # Differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Calculate the distance
    distance = R * c
    
    return distance





def latlon2uv_dir(lat,lon,dt,direction):
    """
    forward/backward differences

    convert time series of lon and lat into time series of u and v
    using haversine

    lon, lat: xarray DataArrays, degrees
    dt: time step between observations

    u, v: xarray DataArrays, m/s
    """
    xr_var = lat


    lat2 = lat.roll({lat.dims[0]: -1}).values
    lon2 = lon.roll({lon.dims[0]: -1}).values
    lat=lat.values
    lon=lon.values
    if direction=='back':
        lon=np.flipud(lon)
        lon2=np.flipud(lon2)
        lat=np.flipud(lat)
        lat2=np.flipud(lat2)

    dr = np.array([haversine(lat[i],lon[i],lat2[i],lon2[i]) for i in range(len(lon))])

    xx=np.sin(np.deg2rad(lon2-lon))*np.cos(np.deg2rad(lat2))
    yy=np.cos(np.deg2rad(lat))*np.sin(np.deg2rad(lat2))-np.sin(np.deg2rad(lat))*np.cos(np.deg2rad(lat2))*np.cos(np.deg2rad(lon-lon))

    gamma=np.arctan2(yy,xx)
    
    if direction=='back':
        dr = np.flipud(dr)
        gamma = np.flipud(gamma)
    

    u=dr/dt*np.cos(gamma)
    v=dr/dt*np.sin(gamma)

    # Edge correction
    u[0] = np.nan
    u[-1] = np.nan
    v[0] = np.nan
    v[-1] = np.nan
    
    u_da = xr.DataArray(u, dims=xr_var.dims, coords=xr_var.coords, name='u')
    v_da = xr.DataArray(v, dims=xr_var.dims, coords=xr_var.coords, name='v')
    speed_da = dr/dt

    return speed_da, u_da, v_da






def downsample_trajectories(df,res):
    '''
    description: given a DataFrame resamples it at the chosen frequency
    IN:
        - df: DataFrame
        - res: String with the resolution desired
    OUT:
        - alldata: DataFrame resampled
    '''
    alldata = pd.DataFrame()
    for i in range(len(df.particle.unique())): 
        # loop over drifters
        temp_df = df[df.particle==i] 
        tempp = temp_df.resample(res).bfill(limit=1).interpolate('pchip') # if resampling has gaps, fill with last entry!
        # reindexing not necessary
        tempp.loc[:,'time'] = tempp.index
        tempp.set_index('particle',inplace=True)
        tempp.loc[:,'particle'] = tempp.index
        # concat multiple drifters
        alldata = pd.concat( [alldata,tempp] )
    return alldata