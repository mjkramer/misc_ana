#!/usr/bin/env python3

import argparse
from glob import glob
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_base")
    args = ap.parse_args()

    study = os.path.basename(args.input_base)

    for direc in sorted(glob(f"{args.input_base}_*")):
        parts = direc.split("/")[-1].split("_")
        if len(parts) != len(study.split("_")) + 1:
            # skip other studies whose names start with $study_
            continue
        cut_mev = float(parts[-1][:-3])

        print(f"{os.path.abspath(direc)} {cut_mev:.3f}")


if __name__ == '__main__':
    main()
