'''
Open mean sea level pressure data --> Find relative max and min --> Create automatic text set up.

author: larsas@met.no


https://github.com/ecjoliver/stormTracking/blob/4a6a56a6d7b2b0fc1831d96126ee92d6b3f6a7bf/storm_functions.py#L43
'''
#Modules
import numpy as np
import sys
from netCDF4 import Dataset
from scipy.signal import argrelmin, argrelmax
from detect_storms import *

path = '/lustre/storeB/project/fou/om/STP40/met_synoptic/era5_atm_CDS_201901_msl_area.nc'

openparameter = Dataset(path, mode = 'r')

parameter = openparameter.variables['msl'][:2,110:180,270:350]
lons = openparameter.variables['longitude'][270:350]
lats = openparameter.variables['latitude'][110:180]

print(np.shape(parameter))
print(np.shape(lons),np.shape(lats))

#Change to hPa and integers
mslpday0 = (parameter[0,:,:]/100)#.astype(int)
mslpday1 = (parameter[1,:,:]/100)#.astype(int)

lon_storms, lat_storms, amp_storms = detect_storms(mslpday0,lons,lats,res=0.25,Npix_min=9,cyc='cyclonic',globe=False)
print(lon_storms, lats_storms, amp_storms)
#np.set_printoptions(threshold=sys.maxsize)

#print(mslpday0)#,mslpday1)

#maxpoints0 = argrelmax(mslpday0)
#print('maxpoints day 0:',maxpoints0)
#maxpoints1= argrelmax(mslpday1)
#print('maxpoints day 1:',maxpoints1)

#minpoints0 = argrelmin(mslpday0)
#minpoints1 = argrelmin(mslpday1)
#print('minpoints day 0:',minpoints0)
#print('minpoint:',mslpday0[15,15])
#print(mslpday0[0,18])
#print('minpoints day 1:',minpoints1)

