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
    ap.add_argument("study")
    ap.add_argument("--toy-opts", default="")
    ap.add_argument("--timeout-mins", type=float, default=85)
    args = ap.parse_args()

    reader = LockfileListReader(
        args.listfile,
        chunksize=1,
        timeout_mins=args.timeout_mins)

    writer = LockfileListWriter(args.listfile + ".done",
                                chunksize=1)

    with writer:
        for line in reader:
            if random.random() < 0.1:
                sysload()

            template_dir, title, cut_str = line.strip().split()
            outdir_name = f"{args.study}/{title}"
            os.system(f"./run_fitter.py {template_dir} {outdir_name} " +
                      f"--cuts {cut_str} {args.toy_opts}")
            writer.log(line)


if __name__ == '__main__':
    unbuf_stdout()
    main()
