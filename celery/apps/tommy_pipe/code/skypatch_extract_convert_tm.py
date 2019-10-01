# -*- coding: utf-8 -*-
"""
This is bldata_conveert_extract.py
This script:
1. gets bl fil files
2. converts filename details
3. converts to 8b
4. makes plot of poitnings
5. makes csv file


Created on Fri Aug 23 17:28:35 2019

@author: tommy
"""



import matplotlib

import numpy as np
import pylab as plt
import pandas as pd
from astropy.coordinates import SkyCoord, Angle

####################################################################
# Read Spider CSV fil

#fn = '/datax2/users/mar855/data/docs/tommy_selection.csv'
fn = '/home/obs/logs/spiderdb/spiderfil_current.csv'
d = pd.read_csv(fn)

#####################################################################   
# Select out files at 21-cm wavelength, HTR data (352 chans)

dsel = d[d['fch1'] == 1361.5]
dsel = dsel[dsel['nchans'] == 352]
dsel = dsel[['src_raj', 'src_dej', 'filepath', 'host']]

#############################################################################
# Convert RA/DEC strings into astropy Coordinates
# This should produce a plot of pointings/beams

sc = SkyCoord(dsel['src_raj'], dsel['src_dej'], unit=('hourangle', 'deg'))
# plt.scatter(sc.galactic.l, sc.galactic.b, marker='.')

#############################################################################  
# Create pulsar dictionary
# Read string and create PSR_NAME:Coordinates

psrs =



"""
eg.
798 J1935+1616 19:35:47.8259 +16:16:39.986 52.44 -2.09 57.8
799 J1752-2806 17:52:58.6896 -28:06:37.3 1.54 -0.96 47.8
807 J1932+1059 19:32:13.9497 -28:06:37.3 47.38  -3.88 28.7
822 J1921+2153 19:21:44.815 +21:53:02.25 55.78   3.50 18.8
823 J1807-0847 18:07:38.0274 -08:47:43.27 20.06 5.59 18.2
831 J1848-0123 18:48:23.5895 -01:23:58.33 31.34 0.04 15.2
833 J1803-2137 18:03:51.4105 -21:37:07.351  8.40 0.15 15
842 J1939+2134 19:39:38.5612 +21:34:59.125 57.51 -0.29 13.2
851 J1829-1751 18:29:43.137 -17:51:03.9 14.60 -3.42 11.0
855 J1825-0935 18:25:30.629 -09:35:22.3 21.45 1.32 10.2
"""

psrdict = {}
for psr in psrs.split('\n'):
    idx, pname, pra, pdec, pl, pb, ps = psr.split()
    psrdict[pname] = SkyCoord(pra, pdec, unit=('hourangle', 'deg'))
    
#############################################################################
# FInd closest pointing
    
def find_closest_pointing(pc):
    """ Print SCP command for closest pulsars """
    idx = np.argmin(np.abs(sc.ra - pc.ra)**2 + np.abs(sc.dec - pc.dec)**2)
    dc = dsel.iloc[idx]
    return "scp " + dc['host'] + ':' + dc['filepath'] + "./"
for psr in psrdict:
    print find_closest_pointing(psrdict[psr])

"""
scp blc16:/datax/PKSMB/GUPPI/guppi_58577_81459_084440_G14.12-3.44_0001.0001.stokesI.8b.fil./
scp blc20:/datax/PKS_0329_2018-07-10T06:00/guppi_58309_39047_229562_G21.47+2.42_0001.0001.fil./
scp blc32:/datax/PKS_0325_2018-07-04T02:00/guppi_58303_39819_013591_G8.40+1.21_0001.0001.fil./
scp blc20:/datax/PKS_0329_2018-07-10T06:00/guppi_58309_55066_236246_G56.82+0.20_0001.0001.fil./
scp blc04:/datax/PKS_0331_2018-07-25T08:00/guppi_58324_47519_773830_G55.88+3.84_0001.0001.fil./
scp blc22:/datax/PKSMB/GUPPI/guppi_58579_73109_153054_G12.60-6.06_0001.0001.stokesI.8b.fil./
scp blc24:/datax/PKS_0333_2018-07-27T10:00/guppi_58326_48905_846506_G20.77+6.06_0001.0001.fil./
scp blc02:/datax/PKS_0326_2018-07-05T03:00/guppi_58304_45557_052034_G31.27+0.00_0001.0001.fil./
scp blc02:/datax/PKS_0327_2018-07-06T04:00/guppi_58305_49487_089722_G52.38-2.22_0001.0001.fil./
scp blc02:/datax2/PKS_0307_2018-05-30T08:00/guppi_58268_40197_079927_G1.52-1.01_0001.0001.fil./
"""

####################################################################
# Data conversion notes
# A lot of data is in 32-bit 4-Stokes filterbanks. Needs conversion into 8-bit Stokes-I. I used these commands:
# (obs) obs@blc00:~/tiddalik/celery/apps/convert_htr_data$ singularity run --bind /datax,/datax2 --nv convert_htr.simg /datax2/users/mar855/psr_top_ten_targets/guppi_58304_45557_052034_G31.27+0.00_0001.0001.fil
# (obs) obs@blc00:~/tiddalik/celery/apps/sum_fil_8b$ singularity run --bind /datax,/datax2 --nv sum_fil_8b.simg /datax2/users/mar855/psr_top_ten_targets/guppi_58304_45557_052034_G31.27+0.00_0001.0001.stokesI.fil

####################################################################
# 2D data selection
ll0 = 358.5 # Centre l
llpm = 1.5  # +/- 1.5 degrees 
bb0 = -1.2  # Centre b
bbpm = 0.4  # +/- 0.8

####################################################################
# Make the two cuts:
# abs(l - ll0) < llpm and abs(b - bb0) < bbpm
sc_cut = sc[np.abs(sc.galactic.l.value - ll0) < llpm]
sc_cut = sc_cut[np.abs(sc_cut.galactic.b.value - bb0) < bbpm]
len(sc_cut)

####################################################################
# Apply cut to data selection
dsel_cut = dsel[np.logical_and(np.abs(sc.galactic.l.value - ll0) < llpm, np.abs(sc.galactic.b.value - bb0) < bbpm)]
dsel_cut.to_csv('tommy_test_selection.csv')

