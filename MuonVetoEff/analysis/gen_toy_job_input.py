#!/usr/bin/env python3

import argparse

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template_dir")
    ap.add_argument("min_pe", type=float)
    ap.add_argument("max_pe", type=float)
    ap.add_argument("n_pe", type=int)
    ap.add_argument("min_sec", type=float)
    ap.add_argument("max_sec", type=float)
    ap.add_argument("n_sec", type=int)
    args = ap.parse_args()

    for pe in np.linspace(args.min_pe, args.max_pe, args.n_pe):
        for sec in np.linspace(args.min_sec, args.max_sec, args.n_sec):
            print(f"{args.template_dir} {pe} {sec}")


if __name__ == '__main__':
    main()
