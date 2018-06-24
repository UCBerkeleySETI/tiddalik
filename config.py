# Some setup vals
compute_nodes = ['blc00', 'blc01', 'blc02', 'blc03', 'blc04', 'blc05']
data_path = "/datax/P999/GUPPI"

rpis = ['rpi%i' % ii for ii in range(0,13)]

extended_nodes = ['blc%i%i' % (ii, jj) for ii in (0,1,2) for jj in (0,1,2,3,4,5,6,7)]
extended_nodes += ['blc30', 'blc31', 'blc32']

storage_nodes = ['bls0', 'bls1', 'bls2', 'bls3']
all_nodes = extended_nodes + storage_nodes
#all_nodes = all_nodes[1:]

# Don't use MB00!
#mb_nodes = extended_nodes[1:]
mb_nodes = extended_nodes[0:]

storage_10gb = {
    #'bls0': '10.10.10.32',
    #'bls1': '10.10.10.33',
    #'bls2': '10.10.10.x',
    'bls3': '10.10.10.10'
}

storage_mnt_points = ['/datax', '/datax2', '/datax3']


beam_mapping = { 
    'blc01': 1,
    'blc02': 1,
    'blc03': 2,
    'blc04': 2,
    'blc05': 3,
    'blc06': 3,
    'blc07': 4,
    'blc10': 4,
    'blc11': 5,
    'blc12': 5,
    'blc13': 6,
    'blc14': 6,
    'blc15': 7,
    'blc16': 7,
    'blc17': 8,
    'blc20': 8,
    'blc21': 9,
    'blc22': 9,
    'blc23': 10,
    'blc24': 10,
    'blc25': 11,
    'blc26': 11,
    'blc27': 12,
    'blc30': 12,
    'blc31': 13,
    'blc32': 13,
    }

# Set library and python birtualenvs
LDL = 'LD_LIBRARY_PATH=/usr/local/gcc-5.4/lib64/:/usr/local/cuda-8.0/lib64:/usr/local/lib:/usr/local/hdf5/lib:/usr/local/lib'
DCPY = 'source /opt/pyve/activate dcpy; '

sigproc_sum_fil_path = '/usr/local/sigproc/bin/sum_fil'
