# Filtering IOs code by Elisabet and Laura

import numpy
from datetime import datetime, timedelta
from netCDF4 import Dataset
import xarray as xr
import scipy.signal as signal
from scipy.signal import butter, filtfilt
from read_data_tools import latlon2uv_dir
import matplotlib.gridspec as gridspec

import cartopy
import cartopy.crs as ccrs
import cartopy.feature       as cfeature
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter
import matplotlib.pylab as plt
# Turn interactive plotting off
# (so have option to save figure without displaying it in the jupyter notebook)
# ((https://stackoverflow.com/questions/15713279/calling-pylab-savefig-without-display-in-ipython))
plt.ioff()

def butter_highpass_filter(data, cutoff, fs, order=5):
    """
    Aplica un filtro Butterworth de paso alto.
   
        Args:
        - data: Array de datos a filtrar.
        - cutoff: Frecuencia de corte del filtro.
        - fs: Frecuencia de muestreo de los datos.
        - order: Orden del filtro.
    
        Returns:
        - y: Datos filtrados.
    
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def filt_ios_butter(infile, drifter_type, cuttof_frequency = 1/36., outdir=None, plot_output="no", savefigdir=None):
    """
    infile  : input netcdf file of drifter to be filtered, e.g. infile = '/home/clement/Downloads/drifter_carthe007-ime_carthe002.nc'
    drifter_type: "C", "H" or "S" (CARTHE, HEREON or SVP-B)
    cuttof_frequency = 1/36. # 31 hores
    outdir : Specify None if you don't want to save. Else, put directory to save data
            , e.g.: '/Users/Gomez023/Library/CloudStorage/OneDrive-UniversitatdelesIllesBalears/FaSt-SWOT/Data/in_situ/analyses/drifters/HEREON/'
    plot_output: "yes" or "no" to plot output of filtering. No by default
    savefigdir: None by default. Define outdir (savename defined automatically) to plot output of filtering. 
    E.g., '/Users/Gomez023/Library/CloudStorage/OneDrive-UniversitatdelesIllesBalears/FaSt-SWOT/Figures/Drifters/IOs/CU_filt/'
    """
   
    ds = xr.open_dataset(infile)
    
    if (drifter_type == "C") | (drifter_type == "H"):
        fs = 6. # mostreig cada 10 mins en comptes de 1h!
        temp_res = 600. # 10 mins. in seconds (temporal resolution of data)
    elif drifter_type == "S":
        fs = 1. # sampling every 1 hour
        temp_res = 3600. # 1 hour in seconds (temporal resolution of data)
    else:
        print ('drifter type error')
        gdfg
    
    lon_filtered = butter_highpass_filter(ds.LON, cuttof_frequency, fs)
    lat_filtered = butter_highpass_filter(ds.LAT, cuttof_frequency, fs)

    # New dataset:
    ds_out = ds.copy(deep=True)
    
    ds_out['LON'][:] = lon_filtered
    ds_out['LAT'][:] = lat_filtered

    # Recaulculating u and v:
    speed, ufor, vfor = latlon2uv_dir(ds_out.LAT, ds_out.LON, temp_res, 'forward')
    _, uback, vback = latlon2uv_dir(ds_out.LAT, ds_out.LON, temp_res, 'back')
    # Calculate central value
    u = (ufor + uback) / 2
    v = (vfor + vback) / 2

    ds_out['U'][:] = u
    ds_out['V'][:] = v

    # Defining outname for saving figures and/or netcdf:
    if (drifter_type == "C") | (drifter_type == "H"):  
        outname = 'drifter-' + infile.split('/')[-1].split('.')[0].split('_')[-1] + '_inertial_osc_filt_v2'
    elif drifter_type == "S":
        outname = infile.split('/')[-1].split('.')[0] + '_inertial_osc_filt_v2'
    else:
        print("Specify drifter type: C, H or S")
        sdfsd

    if (plot_output == 'yes') | (savefigdir != None):
        fig = plt.figure(figsize=(14,10))
        gs = gridspec.GridSpec(4, 2) #, width_ratios=[.33, .33, .33, .01])
        
        ax1 = plt.subplot(gs[0,0])
        ax1.plot(ds.time, ds.LON, c='C0', label='Original lon.')
        ax1.plot(ds.time, lon_filtered, c='C3', label='Filtered lon.')
        plt.ylabel('Longitude (degrees East)')
        plt.legend()
        ax1.set_xticklabels([])
        plt.grid()

        ax1 = plt.subplot(gs[1,0])
        ax1.plot(ds.time, ds.LAT, c='C0', label='Original lat.')
        ax1.plot(ds.time, lat_filtered, c='C3', label='Filtered lat.')
        plt.ylabel('Latitude (degrees East)')
        #plt.legend()
        plt.grid()
        ax1.set_xticklabels([])

        ax1 = plt.subplot(gs[2,0])
        ax1.plot(ds.time, ds.U, c='C0', label='Original lat.')
        ax1.plot(ds.time, ds_out.U, c='C3', label='Filtered lat.')
        plt.ylabel('U (m/s)')
        #plt.legend()
        plt.grid()
        ax1.set_xticklabels([])

        ax1 = plt.subplot(gs[3,0])
        ax1.plot(ds.time, ds.V, c='C0', label='Original lat.')
        ax1.plot(ds.time, ds_out.V, c='C3', label='Filtered lat.')
        plt.ylabel('V (m/s)')
        plt.xticks(rotation=25)
        plt.xlabel('Date (YYYY-MM-DD)')
        #plt.legend()
        plt.grid()

        ax1 = plt.subplot(gs[:,1], projection=ccrs.PlateCarree())
        fsize = 12 # fontsize
        #############
        # Land
        feature = cartopy.feature.NaturalEarthFeature(name='coastline', category='physical',
                                                    scale='10m', zorder=2,
                                                    edgecolor='black', facecolor='#AAAAAA')
        ax1.add_feature(feature)
        #############
        # Grid and ticks
        gl = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                        linewidth=0.5, color='gray', linestyle='-') #, alpha=0.5

        gl.top_labels = False
        gl.right_labels = False

        gl.xlabel_style = {'size': fsize}#, 'color': 'gray'}
        gl.ylabel_style = {'size': fsize}#, 'color': 'gray'}
        #############

        ax1.plot(ds.LON, ds.LAT, transform=ccrs.PlateCarree(), c='C0', label='Proc.') 
        ax1.scatter(ds.LON[0], ds.LAT[0], c='C3', edgecolor='k', linewidths=0.8, transform=ccrs.PlateCarree(), label='Start', zorder=50)
        ax1.plot(ds_out.LON, ds_out.LAT, transform=ccrs.PlateCarree(), c='C3', label='Proc. + filtered') 

        thresa = .1
        map_extent_zoom = [ds.LON.min().values - thresa, ds.LON.max().values + thresa, ds.LAT.min().values - thresa, ds.LAT.max().values + thresa]
        ax1.set_extent(map_extent_zoom, crs=ccrs.PlateCarree())
        
        ax1.legend()#zorder=100)
        
        if savefigdir:
            savename = outname  + '.jpg'
            plt.savefig(savefigdir + savename, dpi=300)
            print('Fig. saved at: ' + savefigdir + savename)
        if plot_output == 'yes':
            plt.show()

        plt.close(fig)
    
    if outdir:

        outfile = outdir + outname + '.nc'
        ds_out.to_netcdf(outfile)
        print('Output file saved at: ' + outfile)
                
        return u, v
    
    else:
        return u, v



