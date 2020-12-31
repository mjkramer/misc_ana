#!/usr/bin/env python3

import argparse

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("min_mev", type=float)
    ap.add_argument("max_mev", type=float)
    ap.add_argument("n_mev", type=int)
    args = ap.parse_args()

    for mev in np.linspace(args.min_mev, args.max_mev, args.n_mev):
        print(f"{mev}")


if __name__ == '__main__':
    main()
