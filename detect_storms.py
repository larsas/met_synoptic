import numpy as np
import scipy as sp
import scipy.ndimage as ndimage
from datetime import date
from itertools import repeat

def detect_storms(field, lon, lat, res, Npix_min, cyc, globe=False):
    '''
    Detect storms present in field which satisfy the criteria.
    Algorithm is an adaptation of an eddy detection algorithm,
    outlined in Chelton et al., Prog. ocean., 2011, App. B.2,
    with modifications needed for storm detection.
    field is a 2D array specified on grid defined by lat and lon.
    res is the horizontal grid resolution in degrees of field
    Npix_min is the minimum number of pixels within which an
    extremum of field must lie (recommended: 9).
    cyc = 'cyclonic' or 'anticyclonic' specifies type of system
    to be detected (cyclonic storm or high-pressure systems)
    globe is an option to detect storms on a globe, i.e. with periodic
    boundaries in the West/East. Note that if using this option the 
    supplied longitudes must be positive only (i.e. 0..360 not -180..+180).
    Function outputs lon, lat coordinates of detected storms
    '''

    len_deg_lat = 111.325 # length of 1 degree of latitude [km]

    # Need to repeat global field to the West and East to properly detect around the edge
    if globe:
        dl = 20. # Degrees longitude to repeat on East and West of edge
        iEast = np.where(lon >= 360. - dl)[0][0]
        iWest = np.where(lon <= dl)[0][-1]
        lon = np.append(lon[iEast:]-360, np.append(lon, lon[:iWest]+360))
        field = np.append(field[:,iEast:], np.append(field, field[:,:iWest], axis=1), axis=1)

    llon, llat = np.meshgrid(lon, lat)

    lon_storms = np.array([])
    lat_storms = np.array([])
    amp_storms = np.array([])

    # ssh_crits is an array of ssh levels over which to perform storm detection loop
    # ssh_crits increasing for 'cyclonic', decreasing for 'anticyclonic'
    ssh_crits = np.linspace(np.nanmin(field), np.nanmax(field), 200)
    ssh_crits.sort()
    if cyc == 'anticyclonic':
        ssh_crits = np.flipud(ssh_crits)

    # loop over ssh_crits and remove interior pixels of detected storms from subsequent loop steps
    for ssh_crit in ssh_crits:
 
    # 1. Find all regions with eta greater (less than) than ssh_crit for anticyclonic (cyclonic) storms (Chelton et al. 2011, App. B.2, criterion 1)
        if cyc == 'anticyclonic':
            regions, nregions = ndimage.label( (field>ssh_crit).astype(int) )
        elif cyc == 'cyclonic':
            regions, nregions = ndimage.label( (field<ssh_crit).astype(int) )

        for iregion in range(nregions):
 
    # 2. Calculate number of pixels comprising detected region, reject if not within >= Npix_min
            region = (regions==iregion+1).astype(int)
            region_Npix = region.sum()
            storm_area_within_limits = (region_Npix >= Npix_min)
 
    # 3. Detect presence of local maximum (minimum) for anticylones (cyclones), reject if non-existent
            #print(region)
            interior = ndimage.binary_erosion(region)
            #print(interior)
            #exterior = region.astype(bool) - interior
            exterior = region - interior

            if interior.sum() == 0:
                continue
            if cyc == 'anticyclonic':
                has_internal_ext = field[interior].max() > field[exterior].max()
            elif cyc == 'cyclonic':
                has_internal_ext = field[interior].min() < field[exterior].min()
 
    # 4. Find amplitude of region, reject if < amp_thresh
            if cyc == 'anticyclonic':
                amp_abs = field[interior].max()
                amp = amp_abs - field[exterior].mean()
            elif cyc == 'cyclonic':
                amp_abs = field[interior].min()
                amp = field[exterior].mean() - amp_abs
            amp_thresh = np.abs(np.diff(ssh_crits)[0])
            is_tall_storm = amp >= amp_thresh
 
    # Quit loop if these are not satisfied
            if np.logical_not(storm_area_within_limits * has_internal_ext * is_tall_storm):
                continue
 
    # Detected storms:
            if storm_area_within_limits * has_internal_ext * is_tall_storm:
                # find centre of mass of storm
                storm_object_with_mass = field * region
                storm_object_with_mass[np.isnan(storm_object_with_mass)] = 0
                j_cen, i_cen = ndimage.center_of_mass(storm_object_with_mass)
                lon_cen = np.interp(i_cen, range(0,len(lon)), lon)
                lat_cen = np.interp(j_cen, range(0,len(lat)), lat)
                # Remove storms detected outside global domain (lon < 0, > 360)
                if globe * (lon_cen >= 0.) * (lon_cen <= 360.):
                    # Save storm
                    lon_storms = np.append(lon_storms, lon_cen)
                    lat_storms = np.append(lat_storms, lat_cen)
                    # assign (and calculated) amplitude, area, and scale of storms
                    amp_storms = np.append(amp_storms, amp_abs)
                # remove its interior pixels from further storm detection
                storm_mask = np.ones(field.shape)
                storm_mask[interior.astype(int)==1] = np.nan
                field = field * storm_mask

    return lon_storms, lat_storms, amp_storms
