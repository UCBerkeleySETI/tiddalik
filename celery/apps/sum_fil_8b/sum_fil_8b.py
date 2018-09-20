#!/usr/bin/env python
""" 
# sum_fil_8b.py

Python wrapper for sum_fil, that does some breakthrough-specific sanity checks.

"""

import os
import blimpy as bl

if __name__ == "__main__":
    
    import argparse
    p = argparse.ArgumentParser(description='Convert filterbank data from float-32 to 8-bit')
    p.add_argument('filename', help='filename of input filterbank file.')
    p.add_argument('-t', '--tmax', type=float, help='Skip files with integration length > tmax. Default 0.001s', default=0.001)
    p.add_argument('-o', '--outputdir', type=str, help='Output directory (default same as input filename)', default='')
    p.add_argument('-e', '--ext', type=str, help='Output extension (default is 8b.fil)', default='8b.fil')
    p.add_argument('-q', '--qlen', type=int, help='qlen parameter to pass to sum_fil for bandpass calc. default=10000', default=10000)
    p.add_argument('-d', '--delete_orig', action='store_true', default=False, help='Delete original filterbank')
    p.add_argument('-s', '--skip_tests', action='store_true', default=False, help='Skip sanity checks on header/data size')
    p.add_argument('-O', '--overwrite', action='store_true', default=False, help='Overwrite existing output files (default to skip)')
    args = p.parse_args()
    
    qlen = args.qlen
    ext  = args.ext.strip('.')
    bn   = os.path.basename(args.filename)
    dn   = os.path.dirname(args.filename)

    f_out = os.path.splitext(args.filename)[0] + '.' + ext
    if args.outputdir == '':
        filename_out = os.path.join(dn, f_out)
    else:
        filename_out = os.path.join(args.outputdir, f_out)

    fh = bl.Waterfall(args.filename, max_load=0)

    t_int  = float(fh.header['tsamp'])
    n_bits = int(fh.header['nbits'])
    n_ifs  = int(fh.header['nifs'])
    
    is_good = True
    if t_int > args.tmax:
        print("Time integration in file is longer than tmax, skipping...")
        is_good = False
    if int(n_bits) != 32 and is_good:
        print("File is not 32-bit floating point! Skipping...")
        is_good = False
    if n_ifs != 1 and is_good:
        print("File has multiple IFs, not supported by sum_fil. Skipping...")
        is_good = False
    if args.overwrite is False and os.path.exists(filename_out) and is_good:
        print("Output file already exists. Skipping...")
        is_good = False
    
    if args.overwrite is True and is_good and os.path.exists(filename_out):
        os.remove(filename_out)  # sum_fil crashes if output file exists already

    # Run sum fil if all data input checks pass
    if is_good:
        exe_str = 'sum_fil {fname} -obits 8 -o {fout} -qlen {qlen}'.format(fname=args.filename, fout=filename_out, qlen=qlen)
        print(exe_str)
        os.system(exe_str)

    tests_passed = True
    if args.skip_tests is False and is_good:
        print("Checking output file is as expected...")
        fh2 = bl.Waterfall(filename_out, max_load=0)
        for key, val in fh.header.items():
            if key == 'nbits':
                assert fh2.header['nbits'] == 8
            elif key in ('barycentric', 'pulsarcentric', 'rawdatafile', 'machine_id'):
                pass  # These are not copied by sum_fil, or differ
            else:
                try: 
                    assert fh2.header[key] == val
                except AssertionError:
                    tests_passed = False
                    print("ERROR: {key} differs across files".format(key=key))
        try:
            assert fh.n_ints_in_file == fh2.n_ints_in_file
        except AssertionError:
            tests_passed = False
            print("ERROR: number of integrations in file doesnt match")
   
    if tests_passed and is_good:
        print("All tests passed OK.")
    
    if args.delete_orig and is_good:
        if args.skip_tests is False and tests_passed is True:
            print("Removing %s" % filename)
            os.remove(args.filename)
        else:
            print("Warning: tests not run or failed. Will not delete original file.") 


