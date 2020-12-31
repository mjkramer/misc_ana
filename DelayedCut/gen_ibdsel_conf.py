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
        cut_mev = float(line.strip())
        config["ibdDelayedEmin"] = cut_mev
        config["ibdDmcEminAfter"] = cut_mev
        tag = os.path.basename(args.outdir)
        outfile = f"config.{tag}_{cut_mev:.2f}MeV.txt"
        config.write(f"{args.outdir}/{outfile}")


if __name__ == '__main__':
    main()
