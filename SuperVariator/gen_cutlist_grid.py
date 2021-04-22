#!/usr/bin/env python3

import argparse
from itertools import product

import numpy as np


def main():
    ap = argparse.ArgumentParser()

    cuts = {}

    def add_cut(name, abbrev_name, default):
        ap.add_argument(f"--{name}-min", type=float, default=default)
        ap.add_argument(f"--{name}-max", type=float, default=default)
        ap.add_argument(f"--{name}-count", type=int, default=1)
        cuts[name.replace("-", "_")] = abbrev_name

    add_cut("shower-pe", "showerPE", 3e5)
    add_cut("shower-sec", "showerSec", 0.4004)
    add_cut("delayed-emin-mev", "delayedMin", 6)
    add_cut("prompt-emin-mev", "delayedMax", 0.7)

    args = ap.parse_args()

    def cutattr(cut, attr):
        return getattr(args, f"{cut}_{attr}")

    def gen(cut):
        minval = cutattr(cut, "min")
        maxval = cutattr(cut, "max")
        count = cutattr(cut, "count")
        return np.linspace(minval, maxval, count)

    allpars = product(*[gen(cut) for cut in cuts])

    for pars in allpars:
        title_parts = []
        for i, cut in enumerate(cuts):
            if cutattr(cut, "count") > 1:
                abbrev = cuts[cut]
                val = pars[i]
                title_parts.append(f"{abbrev}_{val:.6g}")
        title = "_".join(title_parts)
        cut_str = ",".join([f"{cut}={pars[i]}"
                            for i, cut in enumerate(cuts)])
        print(f"{title} {cut_str}")


if __name__ == '__main__':
    main()
