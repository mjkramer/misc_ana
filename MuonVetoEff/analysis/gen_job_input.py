#!/usr/bin/env python3

import sys

import numpy as np


def main():
    min_pe, max_pe, n_pe, min_s, max_s, n_s = \
        map(float, sys.argv[1:])

    for pe in np.linspace(min_pe, max_pe, int(n_pe)):
        for s in np.linspace(min_s, max_s, int(n_s)):
            print(f"{pe} {s}")


if __name__ == '__main__':
    main()
