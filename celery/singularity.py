import os

from config import SINGULARITY_EXE, SINGULARITY_IMG, SINGULARITY_FLAGS

def singularity_exec(exec_str, img=None, flags=None):
    exe = SINGULARITY_EXE
    if img is None:
        img = SINGULARITY_IMG
    if flags is None:
        flags = SINGULARITY_FLAGS
    retcode = os.system('{exe} exec {flags} {img} {es}'.format(exe=exe, flags=flags, img=img, es=exec_str))
    return retcode


def singularity_run(args_str, img=None, flags=None, app=None):
    exe = SINGULARITY_EXE
    if img is None:
        img = SINGULARITY_IMG
    if flags is None:
        flags = SINGULARITY_FLAGS
    if app is not None:
        retcode = os.system('{exe} run {flags} {img} {args}'.format(exe=exe, flags=flags, img=img, args=args_str))
    else:
        retcode = os.system('{exe} run --app {app} {flags} {img} {args}'.format(exe=exe, app=app, flags=flags, img=img, args=args_str))
    return retcode


