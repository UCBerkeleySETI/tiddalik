#!/usr/bin/env bash
touch /home/obs/do_not_delete
./worker_control.py start_all_workers
./dispatch_turboseti.py /datax/PKSMB/GUPPI -e 0000.fil
./dispatch_extract_2b_raw.py /datax/PKSMB/GUPPI -e 0000.raw
./dispatch_convert_htr.py  /datax/PKSMB/GUPPI/ -e 0001.fil
./dispatch_upload_to_blpd0.py /datax/PKSMB/GUPPI -e raw2b
