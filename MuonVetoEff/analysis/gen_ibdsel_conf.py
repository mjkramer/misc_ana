#!/usr/bin/env python3

import argparse
import os

# From IbdSel:
from config_file import ConfigFile, template_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cut_list_file")
    ap.add_argument("outdir")
    args = ap.parse_args()

    os.system(f"mkdir -p {args.outdir}")

    config = ConfigFile(template_path())

    for line in open(args.cut_list_file):
        _template_dir, cut_pe, time_s = line.strip().split()
        config["ibdShowerMuChgCut"] = float(cut_pe)
        config["ibdShowerMuPostVeto_us"] = float(time_s) * 1e6
        tag = os.path.basename(args.outdir)
        outfile = f"config.{tag}_{cut_pe}pe_{time_s}s.txt"
        config.write(f"{args.outdir}/{outfile}")


if __name__ == '__main__':
    main()
