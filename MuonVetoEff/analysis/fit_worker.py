#!/usr/bin/env python3

import argparse
import os
import random

# From IbdSel
from prod_util import unbuf_stdout, sysload
from prod_io import LockfileListReader, LockfileListWriter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listfile")
    ap.add_argument("template_dir")
    ap.add_argument("tag")
    ap.add_argument("--toy-opts", default="")
    args = ap.parse_args()

    reader = LockfileListReader(
        args.listfile,
        chunksize=1,
        timeout_mins=float(os.getenv("TIMEOUT_MINS", "60")))

    writer = LockfileListWriter(args.listfile + ".done",
                                chunksize=1)

    with writer:
        for line in reader:
            if random.random() < 0.1:
                sysload()

            cut_pe, time_s = line.strip().split()
            outdirname = f"{args.tag}/{cut_pe}pe_{time_s}s"
            os.system(f"./run_toymc.py {args.template_dir} {outdirname} " +
                      f"--cut-pe {cut_pe} --time-s {time_s} {args.toy_opts}")
            writer.log(line)


if __name__ == '__main__':
    unbuf_stdout()
    main()
