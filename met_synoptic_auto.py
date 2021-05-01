'''
Open mean sea level pressure data --> Find relative max and min --> Create automatic text set up.

author: larsas@met.no
'''
#Modules
import numpy as np
from netCDF4 import Dataset

path = '/lustre/storeB/project/fou/om/STP40/met_synoptic/era5_atm_CDS_201901_msl_area.nc'

openparameter = Dataset(path, mode = 'r')

parameter = openparameter.variables['msl'][:]
lons = openparameter.variables['longitude'][:]
lats = openparameter.variables['latitude'][:]

print(np.shape(parameter))
print(np.shape(lons),np.shape(lats))


mslpday0 = parameter[0,:,:]/100
mslpday1 = parameter[1,:,:]/100
