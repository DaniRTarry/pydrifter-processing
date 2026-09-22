"""
author: @SebEssink
        email: sessink@mit.edu
        @Tarry
        email: drtarry@imedea.uib-csic.es

type: FUNCTION

description: set of tools used to read drifter data

"""

# Load libraries
import numpy as np
import pandas as pd
import xarray as xr



def haversine(lat1,lon1,lat2,lon2):
    """
    Calculates distance in m
    """
    # Radius of the Earth in kilometers
    R = 6371*1e3
    
    #print(lat1)
    #print(lon1)
    #print(lat2)
    #print(lon2)

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = np.radians(lat1), np.radians(lon1), np.radians(lat2), np.radians(lon2)

    
    # Differences in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
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
    
    lat2 = lat.roll({lat.dims[0]: -1})
    lon2 = lon.roll({lon.dims[0]: -1})

    if direction == 'back':
        lon = lon[::-1]
        lon2 = lon2[::-1]
        lat = lat[::-1]
        lat2 = lat2[::-1]

    dr = xr.apply_ufunc(
        haversine,
        lat, lon, lat2, lon2,
        input_core_dims=[[], [], [], []],
        dask='parallelized',
        output_dtypes=[float],
    )


    xx = np.sin(np.deg2rad(lon2 - lon)) * np.cos(np.deg2rad(lat2))
    yy = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lat2)) - np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(lat2)) * np.cos(np.deg2rad(lon2 - lon))
    gamma = np.arctan2(yy, xx)

    # if direction == 'back':
    #     dr = dr[::-1]
    #     gamma = gamma[::-1]

   
    u = dr / dt * np.cos(gamma)
    v = dr / dt * np.sin(gamma)
    
    u_da = xr.DataArray(u, dims=lon.dims, coords=lon.coords, name='u')
    v_da = xr.DataArray(v, dims=lon.dims, coords=lon.coords, name='v')
    speed_da = dr/dt

    return speed_da, u_da, v_da




def latlon2uv_dir_xr(lat,lon,dt,direction):
    """
    forward/backward differences

    convert time series of lon and lat into time series of u and v
    using haversine

    lon, lat: xarray DataArrays, degrees
    dt: time step between observations

    u, v: xarray DataArrays, m/s
    """
    
    lat2 = lat.roll({lat.dims[0]: -1})
    lon2 = lon.roll({lon.dims[0]: -1})

    if direction == 'back':
        lon = lon[::-1]
        lon2 = lon2[::-1]
        lat = lat[::-1]
        lat2 = lat2[::-1]

    dr = xr.apply_ufunc(
        haversine,
        lat, lon, lat2, lon2,
        input_core_dims=[[], [], [], []],
        dask='parallelized',
        output_dtypes=[float],
    )


    xx = np.sin(np.deg2rad(lon2 - lon)) * np.cos(np.deg2rad(lat2))
    yy = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lat2)) - np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(lat2)) * np.cos(np.deg2rad(lon2 - lon))
    gamma = np.arctan2(yy, xx)

    # if direction == 'back':
    #     dr = dr[::-1]
    #     gamma = gamma[::-1]

   
    u = dr / dt * np.cos(gamma)
    v = dr / dt * np.sin(gamma)
    
    u_da = xr.DataArray(u, dims=lon.dims, coords=lon.coords, name='u')
    v_da = xr.DataArray(v, dims=lon.dims, coords=lon.coords, name='v')
    speed_da = dr/dt

    return speed_da, u_da, v_da





def latlon2uv_dir_np(lat,lon,dt,direction):
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
        
    print(lat)
    print(lat2)
    print(lon)
    print(lon2)

    dr = np.array( [haversine(lat[i],lon[i],lat2[i],lon2[i]) for i in range(len(lon))] )

    xx=np.sin(np.deg2rad(lon2-lon))*np.cos(np.deg2rad(lat2))
    yy=np.cos(np.deg2rad(lat))*np.sin(np.deg2rad(lat2))-np.sin(np.deg2rad(lat))*np.cos(np.deg2rad(lat2))*np.cos(np.deg2rad(lon-lon))

    gamma=np.arctan2(yy,xx)
    
    if direction=='back':
        dr = np.flipud(dr)
        gamma = np.flipud(gamma)
    

    u=dr/dt*np.cos(gamma)
    v=dr/dt*np.sin(gamma)
    
    u_da = xr.DataArray(u, dims=xr_var.dims, coords=xr_var.coords, name='u')
    v_da = xr.DataArray(v, dims=xr_var.dims, coords=xr_var.coords, name='v')
    speed_da = dr/dt

    return speed_da, u_da, v_da







def latlon2uv_corr(lat,lon,dt,direction):
    """
    forward/backward differences

    convert time series of lon and lat into time series of u and v
    using haversine

    lon, lat: xarray DataArrays, degrees
    dt: time step between observations

    u, v: xarray DataArrays, m/s
    """
    
    lon2 = lon.roll({lon.dims[0]: -1})
    lat2 = lat.roll({lat.dims[0]: -1})

    if direction == 'back':
        lon = lon[::-1]
        lon2 = lon2[::-1]
        lat = lat[::-1]
        lat2 = lat2[::-1]

    dr = xr.apply_ufunc(
        haversine,
        lat, lon, lat2, lon2,
        input_core_dims=[[], [], [], []],
        dask='parallelized',
        output_dtypes=[float],
    )


    # Cartesian components correctio 
    x_corr = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lon2-lon))
    y_corr = np.sin(np.deg2rad(lat2-lat))


    #gamma = np.arctan2(yy, xx)

    if direction == 'back':
        dr = dr[::-1]
        #gamma = gamma[::-1]

    u = dr / dt * x_corr
    v = dr / dt * y_corr

    u_da = xr.DataArray(u, dims=lon.dims, coords=lon.coords, name='u')
    v_da = xr.DataArray(v, dims=lon.dims, coords=lon.coords, name='v')
    speed_da = xr.DataArray(dr/dt, dims=lon.dims, coords=lon.coords, name='speed')

    return speed_da, u_da, v_da











def latlon2u(lat,lon,dt,direction):
    """
    forward/backward differences

    convert time series of lon and lat into time series of u and v
    using haversine

    lon, lat: xarray DataArrays, degrees
    dt: time step between observations

    u, v: xarray DataArrays, m/s
    """
    
    lon2 = lon.roll({lon.dims[0]: -1})
    lat2 = lat

    if direction == 'back':
        lon = lon[::-1]
        lon2 = lon2[::-1]
        lat = lat[::-1]
        lat2 = lat2[::-1]

    dr = xr.apply_ufunc(
        haversine,
        lat, lon, lat2, lon2,
        input_core_dims=[[], [], [], []],
        dask='parallelized',
        output_dtypes=[float],
    )

    #xx = np.sin(np.deg2rad(lon2 - lon)) * np.cos(np.deg2rad(lat2))
    #yy = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lat2)) - np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(lat2)) * np.cos(np.deg2rad(lon - lon))

    # Cartesian components correctio 
    x_corr = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lon2-lon))
    y_corr = np.sin(np.deg2rad(lat2-lat))


    #gamma = np.arctan2(yy, xx)

    if direction == 'back':
        dr = dr[::-1]
        #gamma = gamma[::-1]

    u = dr / dt
    v = dr / dt * 0

    u_da = xr.DataArray(u, dims=lon.dims, coords=lon.coords, name='u')
    v_da = xr.DataArray(v, dims=lon.dims, coords=lon.coords, name='v')
    speed_da = xr.DataArray(dr/dt, dims=lon.dims, coords=lon.coords, name='speed')

    return speed_da, u_da, v_da





def latlon2v(lat,lon,dt,direction):
    """
    forward/backward differences

    convert time series of lon and lat into time series of u and v
    using haversine

    lon, lat: xarray DataArrays, degrees
    dt: time step between observations

    u, v: xarray DataArrays, m/s
    """
    
    lon2 = lon
    lat2 = lat.roll({lon.dims[0]: -1})

    if direction == 'back':
        lon = lon[::-1]
        lon2 = lon2[::-1]
        lat = lat[::-1]
        lat2 = lat2[::-1]

    dr = xr.apply_ufunc(
        haversine,
        lat, lon, lat2, lon2,
        input_core_dims=[[], [], [], []],
        dask='parallelized',
        output_dtypes=[float],
    )

    #xx = np.sin(np.deg2rad(lon2 - lon)) * np.cos(np.deg2rad(lat2))
    #yy = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lat2)) - np.sin(np.deg2rad(lat)) * np.cos(np.deg2rad(lat2)) * np.cos(np.deg2rad(lon - lon))

    # Cartesian components correctio 
    x_corr = np.cos(np.deg2rad(lat)) * np.sin(np.deg2rad(lon2-lon))
    y_corr = np.sin(np.deg2rad(lat2-lat))


    #gamma = np.arctan2(yy, xx)

    if direction == 'back':
        dr = dr[::-1]
        #gamma = gamma[::-1]

    u = dr / dt * 0
    v = dr / dt 
    
    u_da = xr.DataArray(u, dims=lon.dims, coords=lon.coords, name='u')
    v_da = xr.DataArray(v, dims=lon.dims, coords=lon.coords, name='v')
    speed_da = xr.DataArray(dr/dt, dims=lon.dims, coords=lon.coords, name='speed')

    return speed_da, u_da, v_da





def xy2uv(lat,lon,dt,direction):
    """
    forward/backward differences

    convert time series of lon and lat into time series of u and v
    asuming earth is flat (because it is)

    lat, lon: xarray DataArrays, degrees
    dt: time step between observations

    u, v: xarray DataArrays, m/s
    """

    # Earth radius
    r = 6371*1e3

    # Roll one element of the vector
    lon2 = lon.roll({lon.dims[0]: -1})
    lat2 = lat.roll({lat.dims[0]: -1})

    if direction == 'back':
        lon = lon[::-1]
        lon2 = lon2[::-1]
        lat = lat[::-1]
        lat2 = lat2[::-1]

    # Convert all coordinates into radians
    lat1, lon1, lat2, lon2 = np.radians(lat), np.radians(lon), np.radians(lat2), np.radians(lon2)

    # Convert the latitude and longitude coordinates of both points to 
    # Cartesian coordinates
    x1 = r * np.cos(lat1) * np.cos(lon1)
    y1 = r * np.cos(lat1) * np.sin(lon1)
    x2 = r * np.cos(lat2) * np.cos(lon2)
    y2 = r * np.cos(lat2) * np.sin(lon2)

    # Calculate the displacement in the x, and y directions:
    dx = x2-x1
    dy = y2-y1

    # Calculate the east-west (u) and north-south (v) velocity components using 
    # the displacement and time (dt)
    u = dx/dt 
    v = dy/dt 

    return u,v





def latlon2uv(lat,lon,dt):
    '''apply both forward and backward differences to get centered difference'''
    u1,v1 = latlon2uv_dir(lon,lat,dt,'for')
    u2,v2 = latlon2uv_dir(lon,lat,dt,'back')
    
    # correct the edges!
    u1[-1]=u2[0]
    v1[-1]=v2[0]
    u2[-1]=u1[0]
    v2[-1]=v1[0]

    uv = 0.5*(u1+u2) + 1j*0.5*(v1+v2)
    return uv




def centered_finite_differences(lat,lon,dt):

    # Earth radius
    r = 6371*1e3

    # Roll one element of the vector
    latb = lat.roll({lat.dims[0]: -1})
    latf = lat.roll({lat.dims[0]: 1})
    lonb = lon.roll({lon.dims[0]: -1})
    lonf = lon.roll({lon.dims[0]: 1})

    # Convert into radians
    latb = np.radians(latb)
    latf = np.radians(latf)
    lonb = np.radians(lonb)
    lonf = np.radians(lonf)


    # Convert the latitude and longitude coordinates into Cartesian coordinates
    xb = r * np.cos(latb) * np.cos(lonb)
    xf = r * np.cos(latf) * np.cos(lonf)

    yb = r * np.cos(latb) * np.sin(lonb)
    yf = r * np.cos(latf) * np.sin(lonf)

    # Centered finite differences
    dx = xf - xb
    dy = yf - yb

    u = dx / (2*dt)
    v = dy / (2*dt)

    # Correct edges
    u[-1:1] = np.nan
    v[-1:1] = np.nan

    u_da = xr.DataArray(u, dims=lon.dims, coords=lon.coords, name='u')
    v_da = xr.DataArray(v, dims=lon.dims, coords=lon.coords, name='v')

    return u_da, v_da



    