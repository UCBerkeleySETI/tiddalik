#!/usr/bin/env python

import matplotlib

import numpy as np
import pylab as plt
import pandas as pd
from astropy.coordinates import SkyCoord, Angle
import os


fil_files = """
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58352_33303_606829_G358.17-1.21_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58352_34027_607131_G358.40-1.21_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58352_34335_607260_G359.68-1.01_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58357_23658_783049_G359.57-1.21_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58357_24001_783192_G359.92-1.01_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58357_24339_783334_G359.80-1.21_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58679_31808_037678_G0.00-1.21_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58679_31463_037534_G0.12-1.01_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58680_31934_073779_G0.12-1.01_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58680_32280_073924_G0.00-1.21_0001.0001.stokesI.8b.fil blc04
/datax/PKSMB/GUPPI/guppi_58352_31539_606093_G356.88-1.01_0001.0001.stokesI.8b.fil blc14
/datax/PKSMB/GUPPI/guppi_58352_32579_606527_G357.12-1.01_0001.0001.stokesI.8b.fil blc14
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc14
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc14
/datax/PKSMB/GUPPI/guppi_58352_21050_601717_G357.82-2.22_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_21736_602003_G358.87-2.42_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_20366_601431_G357.58-2.22_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_20709_601575_G357.47-2.42_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_21389_601858_G357.70-2.42_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_23215_602620_G358.98-2.22_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_23557_602763_G359.22-2.22_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_23899_602905_G359.10-2.42_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58357_37193_788697_G358.87+0.00_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58357_37894_788989_G359.10+0.00_0001.0001.stokesI.8b.fil blc24
/datax/PKSMB/GUPPI/guppi_58352_31539_606093_G356.88-1.01_0001.0001.stokesI.8b.fil blc30
/datax/PKSMB/GUPPI/guppi_58352_32579_606527_G357.12-1.01_0001.0001.stokesI.8b.fil blc30
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc30
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc30
/datax/PKSMB/GUPPI/guppi_58352_31539_606093_G356.88-1.01_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_31880_606235_G356.77-1.21_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_32227_606380_G357.00-1.21_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_32579_606527_G357.12-1.01_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_33303_606829_G358.17-1.21_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc12
/datax/PKSMB/GUPPI/guppi_58352_34027_607131_G358.40-1.21_0001.0001.stokesI.8b.fil blc12
/datax3/collate_mb/PKS_0306_2018-05-29T07:00/blc02/guppi_58267_41079_044247_G0.00-1.21_0001.0001.fil bls3
/datax3/collate_mb/PKS_0306_2018-05-29T07:00/blc04/guppi_58267_40736_044103_G0.12-1.01_0001.0001.fil bls3
/datax3/collate_mb/PKS_0306_2018-05-29T07:00/blc04/guppi_58267_41079_044247_G0.00-1.21_0001.0001.fil bls3
/datax3/collate_mb/PKS_0306_2018-05-29T07:00/blc16/guppi_58267_40736_044103_G0.12-1.01_0001.0001.fil bls3
/datax3/collate_mb/PKS_0306_2018-05-29T07:00/blc20/guppi_58267_40736_044103_G0.12-1.01_0001.0001.fil bls3
/datax/PKSMB/GUPPI/guppi_58352_32579_606527_G357.12-1.01_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58352_33303_606829_G358.17-1.21_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58352_34027_607131_G358.40-1.21_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58352_34335_607260_G359.68-1.01_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58357_23658_783049_G359.57-1.21_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58357_24339_783334_G359.80-1.21_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58357_24001_783192_G359.92-1.01_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58679_31808_037678_G0.00-1.21_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58680_32280_073924_G0.00-1.21_0001.0001.stokesI.8b.fil blc02
/datax/PKSMB/GUPPI/guppi_58352_34335_607260_G359.68-1.01_0001.0001.stokesI.8b.fil blc22
/datax/PKSMB/GUPPI/guppi_58352_34335_607260_G359.68-1.01_0001.0001.stokesI.8b.fil blc06
/datax/PKSMB/GUPPI/guppi_58358_20937_817963_G357.47+0.00_0001.0001.stokesI.8b.fil blc32
/datax/PKSMB/GUPPI/guppi_58358_21285_818108_G357.70+0.00_0001.0001.stokesI.8b.fil blc32
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc16
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc16
/datax/PKSMB/GUPPI/guppi_58352_34335_607260_G359.68-1.01_0001.0001.stokesI.8b.fil blc16
/datax/PKSMB/GUPPI/guppi_58357_24001_783192_G359.92-1.01_0001.0001.stokesI.8b.fil blc16
/datax/PKSMB/GUPPI/guppi_58679_31463_037534_G0.12-1.01_0001.0001.stokesI.8b.fil blc16
/datax/PKSMB/GUPPI/guppi_58680_31934_073779_G0.12-1.01_0001.0001.stokesI.8b.fil blc16
/datax/PKSMB/GUPPI/guppi_58352_32944_606679_G358.28-1.01_0001.0001.stokesI.8b.fil blc20
/datax/PKSMB/GUPPI/guppi_58352_33670_606982_G358.52-1.01_0001.0001.stokesI.8b.fil blc20
/datax/PKSMB/GUPPI/guppi_58357_24001_783192_G359.92-1.01_0001.0001.stokesI.8b.fil blc20
/datax/PKSMB/GUPPI/guppi_58679_31463_037534_G0.12-1.01_0001.0001.stokesI.8b.fil blc20
/datax/PKSMB/GUPPI/guppi_58680_31934_073779_G0.12-1.01_0001.0001.stokesI.8b.fil blc20
"""

for fil_file in str(fil_files.split('\n')):
    line = str(fil_file.split(" ",0))
    filepath = str(line.split(".fil",0))
    print(filepath)
    


'''
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
'''
