#!/usr/bin/env python

import os
import time
import argparse
import xml.etree.ElementTree as xmlt

def get_source_name_from_header(froot):
    """ Get source name from .header file """
    hdr_file_name = os.path.basename(froot) + ".header"
    hdr_file = open(hdr_file_name, "r")
    hdr_data = hdr_file.readlines()
    source_name = hdr_data[0].strip("\n")
    if source_name == "": source_name = "Unknown"
    return source_name

def read_candidates():
    """ Read candidates from peasoup overview.xml output 
    
    Note: this assumes you're in the same directory as the xml file.
    """
    tree = xmlt.parse('overview.xml')
    root = tree.getroot()
    cands = {}
    for cand in root.findall('candidates/candidate'):
        cand_idx = cand.attrib['id']
        cands[cand_idx] = {}

        for node in cand.getiterator():
            if node.tag == 'period':
                period = float(node.text)
                cands[cand.attrib['id']]['p'] = period
            elif node.tag == 'dm':
                dm = float(node.text)
                cands[cand.attrib['id']]['dm'] = dm
            elif node.tag == 'snr':
                snr = float(node.text)
                cands[cand.attrib['id']]['snr'] = snr
    return cands

def report_candidates(cands):
    """ Print to screen a quick report from a peasoup candidate file 
    
    Args:
        cands (dict): Dictionary of candidates (use read_candidates to generate)
    """
    print("----------------------------")
    print("Number of candidates: {}".format(len(cands)))
    for cand_id, cd in cands.items():
        print('DM: {:2.2f}  \t P: {:2.4f}   \t SNR: {:2.1f}'.format(cd['dm'], cd['p'], cd['snr']))
    print("----------------------------\n")

def gen_prepfold_cmds(cands, src_name, fil_path, nsub=88):
    """ Generate the prepfold commands to run """
    cmds = []
    mask_file = '{}_rfifind.mask'.format(src_name)

    for cidx, cdict in cands.items():
        pf_cmd = 'prepfold -noxwin -ncpus 1'
        if cdict['snr'] >= 10:
            ps_out = 'prepfold_out/{src}_{cidx}.prepfold'.format(src=src_name, cidx=cidx)
            dm, period = cdict['dm'], cdict['p']
            if period < 0.002:
                Mp, Mdm, N = 2, 3, 24
                npart = 50
                otheropts = " "
            elif period < 0.05:
                Mp, Mdm, N = 2, 1, 50
                npart = 40
                otheropts = "-pstep 1 -pdstep 2 -dmstep 3"
            elif period < 0.5:
                Mp, Mdm, N = 1, 1, 100
                npart = 30
                otheropts = "-pstep 1 -pdstep 2 -dmstep 1"
            else:
                Mp, Mdm, N = 1, 1, 200
                npart = 30
                otheropts = "-nopdsearch -pstep 1 -pdstep 2 -dmstep 1"
            pf_cmd += ' -dm {} -nsub {} -npart {} {} -n {} -npfact {} -ndmfact {} -p {} -o {}'.format(dm, nsub, npart, otheropts, N, Mp, Mdm, period, ps_out)

            if os.path.exists(mask_file):
                pf_cmd += ' -mask {}'.format(mask_file)
            pf_cmd += ' {}'.format(fil_path)
            #print(pf_cmd) 
            cmds.append(pf_cmd)
    return cmds

def run_cmds(cmds):
    """ Run a list of commands """
    for ii, cmd in enumerate(cmds):
        print('--- [{}/{}] ---'.format(ii+1, len(cmds)))
        print('>>> {}'.format(cmd))
        os.system(cmd)
        time.sleep(0.5)

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Run prepfold on data')
    p.add_argument('fil', help='Path to filterbank file')
    p.add_argument('-o', dest='outdir', default='/datax2/users/tp', help='output directory root')

    args = p.parse_args()

    fil = args.fil
    froot  = fil.replace('.fil', '')
    outdir = os.path.join(args.outdir, os.path.basename(froot))

    print(outdir)
    os.chdir(outdir)

    if not os.path.exists('prepfold_out'):
        os.mkdir('prepfold_out')

    src_name = get_source_name_from_header(froot)

    cands = read_candidates()
    report_candidates(cands)
    print("-------------------")
    time.sleep(1)

    pf_cmds = gen_prepfold_cmds(cands, src_name, fil) 

    run_cmds(pf_cmds)
