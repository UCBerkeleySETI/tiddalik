#!/usr/bin/env python
""" 
# sum_fil_8b.py

Python wrapper for sum_fil, that does some breakthrough-specific sanity checks.

"""

import blimpy as bl
import pylab as plt
import glob as glob
import os
import numpy as np
import h5py
from astropy.coordinates import SkyCoord
import socket

beam_cal_jy = [34.960548332986086,
             35.489753722027636,
             36.10566197658091,
             38.29833716516338,
             37.04430145046121,
             36.93626827235949,
             35.822576762908085,
             41.946883333436794,
             40.63994318164593,
             41.67812835599238,
             40.07285088926592,
             44.0302690188603,
             45.3518902462294]

idxs = ['01', '03', '05', '07', '11', '13', '15', '17', '21', '23', '25', '27', '31']
beam_map = ['blc{ii}'.format(ii=ii) for ii in idxs]

def get_beam_from_hostname(fn):
    mnt = socket.gethostname()
    beam_id = beam_map.index(mnt) + 1
    return beam_id
    
def extract_21cm(fn):
    off_bp = bl.Waterfall(fn, f_start=1416.0, f_stop=1417.5)
    on_bp  = bl.Waterfall(fn, f_start=1419.5, f_stop=1421.0)
    on_bp.data /= off_bp.data.mean(axis=0)
    on_bp.data -= 1
    
    beam_id = get_beam_from_hostname(fn)
    T_sys = beam_cal_jy[beam_id - 1]
    
    d = {}
    d['f']   = on_bp.generate_freqs(f_start=1419.5, f_stop=1421.0)
    d['ra']  = on_bp.header['src_raj']
    d['dec'] = on_bp.header['src_dej']
    d['d']   = on_bp.data.mean(axis=0).squeeze() * T_sys
    d['lsrk'] = on_bp.compute_lsrk()
    
    return d

def flux1934(f):
    """ Return 1934-638 model flux over freq
    frequency in MHz
    """
    log10 = np.log10
    x   = -30.7667 + 26.4908*log10(f) - 7.0977*(log10(f))**2 + 0.605334*(log10(f))**3
    flux =  10**x
    return flux

def walk_all_dirs():
    dl_all = []
    for bb in beam_map:
        print bb
        path = '/mnt_{host}/'.format(host=bb)
        dl = [x[0] for x in os.walk(path)]
        dl_all.append(dl)
    return dl_all




if __name__ == "__main__":
    
    import argparse
    p = argparse.ArgumentParser(description='Extract 21-cm data from a hires file')
    p.add_argument('filename', help='filename of input filterbank file.')
    p.add_argument('-o', '--outputdir', type=str, help='Output directory (default same as input filename)', default='')
    args = p.parse_args()
    
    bn   = os.path.basename(args.filename)
    dn   = os.path.dirname(args.filename)

    bn_out = os.path.splitext(bn)[0] + '.galaxy.h5'
    if args.outputdir == '':
        filename_out = os.path.join(dn, bn_out)
    else:
        filename_out = os.path.join(args.outputdir, bn_out)

    with h5py.File(args.filename, 'r+') as fh:
        to_extract = False
        f0 = fh['data'].attrs['fch1']
        if np.isclose(f0, 1515.5):
            fh['data'].attrs['fch1'] = 1513.75
            print("Correcting fch1...")
            to_extract = True
        if np.isclose(f0, 1513.75):
            to_extract = True
    if os.path.exists(filename_out):
        to_extract = False
        print("Skipping %s: file exists..." % args.filename)
        
    if to_extract:
        print("Extracting %s" % args.filename) 
        d = extract_21cm(args.filename)
        
        h5_in  = h5py.File(args.filename)
        h5_out = h5py.File(filename_out)
        
        d5_in  = h5_in['data']
        d5_out = h5_out.create_dataset('data', data=d['d'])

        d5_out.attrs['source_name'] = d5_in.attrs['source_name']
        d5_out.attrs['src_raj'] = d5_in.attrs['src_raj']
        d5_out.attrs['src_dej'] = d5_in.attrs['src_dej']
        d5_out.attrs['host']    = socket.gethostname()
        d5_out.attrs['fch1']    = 1421.0
        d5_out.attrs['foff']    = d5_in.attrs['foff']
        d5_out.attrs['lsrk']    = d['lsrk']
        d5_out.attrs['tsamp']   = d5_in.shape[0] * d5_in.attrs['tsamp']
        d5_out.attrs['tstart']  = d5_in.attrs['tstart']
        d5_out.attrs['input_filename'] = args.filename
        d5_out.attrs['input_filename_abs'] = os.path.abspath(args.filename)
        
            
