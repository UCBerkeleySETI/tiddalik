#!/usr/bin/env python
""" Convert hi-time res fullstokes filterbanks into a Stokes-I filterbank and a compressed/archival HDF5 version """

import numpy as np
import h5py
import bitshuffle
import blimpy as bl
from blimpy.sigproc import generate_sigproc_header
import time
import os

#SIGPROC_PATH = '/usr/local/sigproc/bin/'
SIGPROC_PATH = '/usr/bin/'
SUM_FIL = os.path.join(SIGPROC_PATH, 'sum_fil')
HEADER  = os.path.join(SIGPROC_PATH, 'header')



def convert_fil_to_archival(filename_in, h5_out, fb_out, scale_factor=10, gulp_size=32768):
    """ Convert a full-stokes filterbank to HDF5 archival and Stokes I filterbank 
    
    Args:
        filename_in (str): Input file name
        h5_out (str): Output HDF5 archival file name
        fb_out (str): Output Stokes-I filterbank file name
        scale_factor (float): Scaling factor for saving data to file. Larger values give more precision.
        gulp_size (int): Number of time integrations to process at once for bandpass computation.
    """

    t0 = time.time()
    print("----- %s -----" % filename_in)
    with h5py.File(h5_out, 'w') as h5, open(fb_out, 'w') as fb:
        
        print("Setup: preload to read shape...")
        a0      = bl.Waterfall(filename_in, max_load=0)
        n_ints  = a0.n_ints_in_file
        n_gulps = int(n_ints / gulp_size)
        if n_gulps == 0:
            n_gulps = 1
        if n_ints % n_gulps != 0:
            n_gulps = int(n_ints / gulp_size) + 1
        n_chans = int(a0.header['nchans'])
        
        # Write HDF5 header data as attributes
        for key, value in a0.header.items():
            h5.attrs[key] = value
            h5.attrs['scale_factor'] = scale_factor
            h5.attrs['gulp_size']    = gulp_size

        # Generate and write sigproc header (AFTER ORIG)
        a0.header['nifs'] = 1
        sp_header = generate_sigproc_header(a0)
        fb.write(sp_header)
 
        # Generate HDF5 dsets
        dset_names    = ['xx', 'yy', 're_xy', 'im_xy']
        bp_dset_names = ['bp_xx', 'bp_yy', 'bp_re_xy', 'bp_im_xy']
        for dset_name in bp_dset_names:
            dataset = h5.create_dataset(dset_name, shape=(n_gulps, n_chans), dtype='float32')
            dataset.dims[0].label = b"gulp_id"
            dataset.dims[1].label = b"frequency"

        for dset_name in dset_names:
            print("Setup: generating HDF5 %s" % dset_name)
            block_size = 0
            dataset = h5.create_dataset(dset_name, shape=(n_ints, n_chans),
            compression=bitshuffle.h5.H5FILTER,
            compression_opts=(block_size, bitshuffle.h5.H5_COMPRESS_LZ4),
            dtype='int32',
            chunks=(8192, 8)
            )
            dataset.dims[0].label = b"time"
            dataset.dims[1].label = b"frequency"
         
        # Loop through gulps and write data
        for ii in range(n_gulps):
            print("[%i / %i] Loading data..." % (ii+1, n_gulps))
            a     = bl.Waterfall(filename_in, t_start=ii*gulp_size, t_stop=(ii+1)*gulp_size)
            
            xx    = a.data[:, 0]
            yy    = a.data[:, 1]
            re_xy = a.data[:, 2]
            im_xy = a.data[:, 3]

            print("[%i / %i] Computing bandpass..." % (ii+1, n_gulps))
            bp_xx    = np.median(xx, axis=0)
            bp_yy    = np.median(yy, axis=0)
            bp_re_xy = np.median(re_xy, axis=0)
            bp_im_xy = np.median(im_xy, axis=0)

            bpass = {
                'bp_xx': bp_xx,
                'bp_yy': bp_yy,
                'bp_re_xy': bp_re_xy,
                'bp_im_xy': bp_im_xy
            }

            print("[%i / %i] Applying bandpass..." % (ii+1, n_gulps))
            spec = {
                'xx'   : (xx - bp_xx) * scale_factor,
                'yy'   : (yy - bp_yy) * scale_factor,
                're_xy': (re_xy - bp_re_xy) * scale_factor,
                'im_xy': (im_xy - bp_im_xy) * scale_factor,
                }    
            
            print("[%i / %i] Writing HDF5..." % (ii+1, n_gulps))
            # Write HDF5 bandpasses
            for dset_name, dset_data in bpass.items():
                dataset = h5[dset_name]
                dataset[ii] = dset_data

            # Write HDF5 spectral data
            for dset_name, dset_data in spec.items():
                dataset = h5[dset_name]
                i0 = ii * gulp_size
                i1 = (ii+1) * gulp_size
                dataset[i0:i1] = np.round(dset_data)
                
            print("[%i / %i] Writing Stokes-I filterbank ..." % (ii+1, n_gulps))
            # Write filterbank file
            sp_data = xx + yy
            np.float32(sp_data.ravel()).tofile(fb)
    
    t1 = time.time()
    print("\n-----\nFile size in:  %iB" % os.path.getsize(filename_in))
    print("HDF5 size out: %iB" % os.path.getsize(h5_out))
    print("Compression factor: %2.2fx" % (1.0 * os.path.getsize(filename_in) / os.path.getsize(h5_out)))
    print("Processing time: %2.2fs" % (t1 - t0))
    print("Done.")


def test_compare_files(filename_in, h5_out, fil_out, gulp_size=32768, threshold=2.0):
    """ Compare output files for validity 

    Args:
        filename_in (str): Name of original file
        h5_out (str): Name of archival HDF5 output file to compare against
        fil_out (str): Name of Stokes-I output file to compare against
        gulp_size (int): Number of integrations used in each gulp
        threshold (float): Maximum percentage deviation allowed in comparsion (default 2pc)
    """
    t0 = time.time()
    a0      = bl.Waterfall(filename_in, max_load=0)
    n_ints  = a0.n_ints_in_file
    n_gulps = int(n_ints / gulp_size)
    if n_ints % n_gulps != 0:
        n_gulps = int(n_ints / gulp_size) + 1
    n_chans = int(a0.header['nchans'])
    
    print("HDF5: checking data shape")
    b = h5py.File(h5_out)
    assert n_ints  == b['xx'].shape[0]
    assert n_chans == b['xx'].shape[-1]
    assert n_ints  == b['yy'].shape[0]
    assert n_chans == b['yy'].shape[-1]
    assert n_ints  == b['re_xy'].shape[0]
    assert n_chans == b['re_xy'].shape[-1]
    assert n_ints  == b['im_xy'].shape[0]
    assert n_chans == b['im_xy'].shape[-1]
    
    print("HDF5: checking metadata...")
    for key, val in a0.header.items():
        assert key in b.attrs
        try:
            if key == 'nifs':
                assert b.attrs[key] == val # Only changed for Stokes-I fil
            elif key in ('src_raj', 'src_dej'):
                assert val.value == b.attrs[key]
            else:
                assert b.attrs[key] == val
        except AssertionError:
            print key, val, b.attrs[key]
            raise
    print("Metadata OK.")
    
    print("Stokes-I filterbank: checking metadata...")
    c0      = bl.Waterfall(fil_out, max_load=0)
    assert c0.n_ints_in_file == n_ints
    assert c0.header['nchans'] == n_chans

    for key, val in a0.header.items():
        assert key in c0.header
        try:
            if key == 'nifs':
                assert int(c0.header[key]) == 1
            elif key in ('src_raj', 'src_dej'):
                assert np.isclose(val.value, c0.header[key].value)
            else:
                assert c0.header[key] == val
        except AssertionError:
            print key, val, c0.header[key]
            raise
    print("Metadata OK.")    

    print("Computing difference percentages and checking StokesI...")
    for ii in range(0, n_gulps):
        i0, i1 = (ii)*gulp_size, (ii+1)*gulp_size
        a = bl.Waterfall(filename_in, t_start=i0, t_stop=i1)
        xx    = a.data[:, 0]
        yy    = a.data[:, 1]
        re_xy = a.data[:, 2]
        im_xy = a.data[:, 3]
    
        scale_factor = b.attrs['scale_factor']
        xxo    = b['xx'][i0:i1] / scale_factor + b['bp_xx'][ii]
        yyo    = b['yy'][i0:i1] / scale_factor + b['bp_yy'][ii]
        re_xyo = b['re_xy'][i0:i1] / scale_factor + b['bp_re_xy'][ii]
        im_xyo = b['im_xy'][i0:i1] / scale_factor + b['bp_im_xy'][ii]
    
        max_diff_xx = np.max(np.abs((xx - xxo) / xx) * 100)
        max_diff_yy = np.max(np.abs((yy - yyo) / yy) * 100)
        
        # Now check StokesI
        c = bl.Waterfall(fil_out, t_start=i0, t_stop=i1)
        try:
            assert np.allclose(c.data.squeeze(), xx + yy)
            print("[%i / %i] Stokes I == XX + YY" % (ii+1, n_gulps))
        except AssertionError:
            print("ERROR: Stokes I data does not match.")
            raise

        try:
            print("[%i / %i] percentage difference (XX and YY): %2.2f, %2.2f" % (ii+1, n_gulps, max_diff_xx, max_diff_yy))
            assert max_diff_xx < threshold
            assert max_diff_yy < threshold
        except AssertionError:
            print("ERROR: fractional difference exceeds threshold!")
    t1 = time.time()
    print("Comparsion time: %2.2fs" % (t1 - t0))


def convert_to_8bit(filename_in, filename_out, overwrite=True, remove_float=True):
    """ Convert filterbank file to 8-bit filterbank 
    
    Runs sum_fil on the data to convert to 8-bits.
    """
    t0 = time.time()

    if not os.path.exists(filename_in):
        print("ERROR: Can't find input file %s" % filename_in)
        return

    print("--- REQUANTIZING %s TO 8-BIT ---" % filename_in)
    if os.path.exists(filename_out):
        if overwrite:
            print("Removing older 8-bit file...")
            os.remove(filename_out)
    
    print("%s %s -obits 8 -o %s -qlen 10000" % (SUM_FIL, filename_in, filename_out))
    ret = os.system("%s %s -obits 8 -o %s -qlen 10000" % (SUM_FIL, filename_in, filename_out))
    t1 = time.time()
    
    if ret == 0:
        if remove_float:
            print("Conversion successful, removing %s..." % fil_out)
            os.remove(fil_out)
    if ret == 0:
        print("Conversion time: %2.2fs" % (t1 - t0))
    else:
        print("ERROR: couldn't convert for some reason.")


def run_sigproc_header(filename):
    """ Run the sigproc HEADER utility on file (useful for quick check) """
    ret = os.system("%s %s" % (HEADER, filename))
    if ret != 0:
        raise RuntimeError("Cannot read header") 


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description='Convert hi-time res data in full-stokes filterbanks to a Stokes-I filterbank and a HDF5 archival file')

    p.add_argument('filename_in', help='Name of input HTR Full-stokes file', type=str)
    p.add_argument('-T', '--runtest', help='Test that output data is good', action='store_true', default=False)
    p.add_argument('-g', '--gulp_size', help='No. of integrations to read per gulp', type=int, default=32768)
    p.add_argument('-s', '--scale_factor', help='Scale factor for compression. Larger = more precision but less compression', type=float, default=10)
    p.add_argument('-q', '--requant', help='Run sum_fil to requantize Stokes-I data into 8-bits', action='store_true', default=False)
    p.add_argument('-S', '--skip_creation', help='Skip actual file creation (for testing purposes)', action='store_true', default=False)
    p.add_argument('-d', '--delete_after_requant', help='Delete interim float32 Stokes-I after requantization', action='store_true', default=False)
    p.add_argument('-D', '--delete_fullstokes_fil', help='Delete fullstokes filterbank file (be careful!!)', action='store_true', default=False)
    args = p.parse_args()

    h5_out = os.path.splitext(args.filename_in)[0] + '.h5x'
    fil_out = os.path.splitext(args.filename_in)[0] + '.stokesI.fil'
    
    t0 = time.time()
    print("-----------------")
    print("Filename in:        %s" % args.filename_in)
    print("Archival HDF5 out:  %s" % h5_out)
    print("StokesI FB out:     %s" % fil_out)

    if not args.skip_creation:
        convert_fil_to_archival(args.filename_in, h5_out, fil_out, scale_factor=args.scale_factor, gulp_size=args.gulp_size)
    
    if args.runtest:
        run_sigproc_header(fil_out)
        test_compare_files(args.filename_in, h5_out, fil_out, gulp_size=args.gulp_size, threshold=2.0)

    if args.requant:
        fil_out_8b = os.path.splitext(fil_out)[0] + '.8b.fil'
        convert_to_8bit(fil_out, fil_out_8b, remove_float=args.delete_after_requant)
        run_sigproc_header(fil_out_8b)
        print("Fullstokes file size:     %iB" % os.path.getsize(args.filename_in))
        print("Stokes-I 8-bit file size: %iB" % os.path.getsize(fil_out_8b))
        print("Size reduction:           %2.2fx" % (1.0 * os.path.getsize(args.filename_in) / os.path.getsize(fil_out_8b)))        
    
    if args.delete_fullstokes_fil:
        final_fil_out = fil_out
        if args.requant:
            final_fil_out = fil_out_8b
        if os.path.exists(final_fil_out) and os.path.exists(h5_out):
            print("Removing %s" % args.filename_in)
            os.remove(args.filename_in)
        else:
            print("WARNING: Can't find all output files, not deleting %s" % args.filename_in) 

    t1 = time.time()
    print("Total time: %2.2fs" % (t1 - t0))
