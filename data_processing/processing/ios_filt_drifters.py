# Filtering IOs code by Clement Ubelmann
## adapted to python function by Laura Gómez Navarro

import numpy
from datetime import datetime, timedelta
from netCDF4 import Dataset
import xarray as xr

import matplotlib.pylab as plt
# Turn interactive plotting off
# (so have option to save figure without displaying it in the jupyter notebook)
# ((https://stackoverflow.com/questions/15713279/calling-pylab-savefig-without-display-in-ipython))
plt.ioff()

def filt_ios(infile, drifter_type, outdir=None, plot_output="no", savefigdir=None):
    """
    infile  : input netcdf file of drifter to be filtered, e.g. infile = '/home/clement/Downloads/drifter_carthe007-ime_carthe002.nc'
    drifter_type: "C", "H" or "S" (CARTHE, HEREON or SVP-B)
    outdir : Specify None if you don't want to save. Else, put directory to save data
            , e.g.: '/Users/Gomez023/Library/CloudStorage/OneDrive-UniversitatdelesIllesBalears/FaSt-SWOT/Data/in_situ/analyses/drifters/HEREON/'
    plot_output: "yes" or "no" to plot output of filtering. No by default
    savefigdir: None by default. Define outdir (savename defined automatically) to plot output of filtering. 
    E.g., '/Users/Gomez023/Library/CloudStorage/OneDrive-UniversitatdelesIllesBalears/FaSt-SWOT/Figures/Drifters/IOs/CU_filt/'
    """
   
    with Dataset(infile, 'r') as fcid:
        if (drifter_type == "C") | (drifter_type == "H"):  
            time = numpy.array(fcid.variables['time'][1:-1]) * 60 # seconds (originally in minutes)
        elif drifter_type == "S":
            time = numpy.array(fcid.variables['time'][1:-1]) * 60 * 60 # seconds (originally in hours)
        else:
            print("Specify drifter type: C, H or S")
            sdfsd

        u = numpy.array(fcid.variables['U'][1:-1])
        v = numpy.array(fcid.variables['V'][1:-1])
        lat = numpy.array(fcid.variables['LAT'][1:-1])
    
    # Checking if the trajectory is shorter than 3 days.
    # (drifter trajectory will be skipped if so, as then the time_conv cannot be done)
    if time[-1] < 3 * 86400: # time in seconds:
        print(infile.split('_')[-1].split('.')[0] + 'drifter trajectory too short to filter (less than 3 days)')
        return numpy.nan, numpy.nan
    
    else: # continue as normal
        U = u + 1j*v
        dt = time[1] - time[0]
        fc = 2 * 2 * numpy.pi/86164 * numpy.sin(lat.mean() * numpy.pi/180)  # s-1

        time_conv = numpy.arange(-3*86400, 3*86400+dt, dt)
        taul = 3 * fc**-1
        # gl = 
        # (numpy.exp(-1j*numpy.outer(fc[:],time_conv))*numpy.exp(-numpy.outer(taul**-2,time_conv**2))).reshape(len(time),len(time_conv))
        gl = numpy.exp(-1j * fc * time_conv) * numpy.exp(-taul**-2 * time_conv**2)
        gl = (gl.T / numpy.sum(numpy.abs(gl), axis=0).T).T

        Unio =numpy.convolve(U, gl, 'same')
        
        # Get u and v components of NIOs (near-inertial oscillations):
        u_nio = numpy.real(Unio)
        v_nio = numpy.imag(Unio)

        if (plot_output == 'yes') | (savefigdir != None):
            fig = plt.figure()
            plt.subplot(211)
            plt.plot(time / 60. / 60. / 24., u, c='k', label='u total')
            plt.plot(time / 60. / 60. / 24., u_nio, c='r', label='u nio')
            plt.plot(time / 60. / 60. / 24., u-u_nio, c='b', label='u res')
            plt.ylabel('u (m/s)')
            plt.legend()
            plt.grid()

            plt.subplot(212)
            plt.plot(time / 60. / 60. / 24., v, c='k', label='v total')
            plt.plot(time / 60. / 60. / 24., v_nio, c='r', label='v nio')
            plt.plot(time / 60. / 60. / 24., v-v_nio, c='b', label='v res')
            plt.ylabel('v (m/s)')
            plt.xlabel('Days since deployement')
            plt.legend()
            plt.grid()
            
            if savefigdir:
                savename = infile.split('/')[-1].split('.')[0] + '_inertial_osc_filt_CU' + '.jpg'
                plt.savefig(savefigdir + savename, dpi=300)
            
            if plot_output == 'yes':
                plt.show()

            plt.close(fig)
    
        if outdir:
            # Add variables to the dataset
            ds00 = xr.open_dataset(infile)
            ds_out = ds00.copy(deep=True)
            ## Ignoring first and last values like Clement above:
            ds_out = ds_out.isel(time=slice(1, -1))
        
            ds_out['U_filt'] = ds_out['U'].copy(deep=True)
            ds_out['V_filt'] = ds_out['V'].copy(deep=True)
            ds_out['U_filt'][:] = u - u_nio
            ds_out['V_filt'][:] = v - v_nio
            # ds_out = ds_out.assign(U_filt=u-u_nio)
            # ds_out = ds_out.assign(V_filt=v-v_nio)

            if (drifter_type == "C") | (drifter_type == "H"):  
                outname = 'drifter-' + infile.split('/')[-1].split('.')[0].split('_')[-1] + '_inertial_osc_filt_CU.nc'
            elif drifter_type == "S":
                outname = infile.split('/')[-1].split('.')[0] + '_inertial_osc_filt_CU.nc'
            else:
                print("Specify drifter type: C, H or S")
                sdfsd
            outfile = outdir + outname
            ds_out.to_netcdf(outfile)
            return u-u_nio, v-v_nio
        
        else:
            return u-u_nio, v-v_nio



