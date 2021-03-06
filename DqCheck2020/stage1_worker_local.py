#!/usr/bin/env python3
"Basically just stage1_worker without calling stage1_fbf_path"

import argparse
import os
import random

from prod_util import parse_path, sysload, phase_for_run, unbuf_stdout
from prod_util import worker_timeout_mins
from zmq_fan import ZmqListReader, ZmqListWriter
from prod_io import LockfileListReader, LockfileListWriter


def get_outpath(outdir, site, runno, fileno):
    return f"{outdir}/stage1.fbf.eh{site}.{runno:07d}.{fileno:04d}.root"


def process(path, outdir):
    runno, fileno, site = parse_path(path)
    phase = phase_for_run(runno)
    outpath = get_outpath(outdir, site, runno, fileno)

    os.system('mkdir -p %s' % os.path.dirname(outpath))

    exe = os.getenv('IBDSEL_HOME') + '/selector/_build/stage1.exe'
    cmd = f'{exe} {path} {outpath} {site} {phase}'
    print(cmd)
    os.system(f'time {cmd}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    ap.add_argument('-i', '--inputlist',
                    help="Access the specified input list directly " +
                    "(via lockfile) instead of using ZMQ fan")
    ap.add_argument('-c', '--chunksize', type=int, default=1,
                    help="Only has an effect when used with -i")
    args = ap.parse_args()

    if args.inputlist:
        reader = LockfileListReader(args.inputlist, chunksize=args.chunksize)
        logger = LockfileListWriter(args.inputlist + ".done",
                                    chunksize=args.chunksize)
    else:
        reader = ZmqListReader(timeout_mins=worker_timeout_mins())
        logger = ZmqListWriter()

    with logger:
        for path in reader:
            if random.random() < 0.01:
                sysload()
            process(path, args.outdir)
            logger.log(path)


if __name__ == '__main__':
    unbuf_stdout()
    main()
