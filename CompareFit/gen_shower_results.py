#!/usr/bin/env python3

import os
from glob import glob

from CompareFit import read_fit_file

FITDIR = "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/fit_output"


def fitdirs():
    return glob(f"{FITDIR}/2020_01_26@shower2*")


def parse_fitdir(fitdir):
    name = os.path.basename(fitdir)
    name = name.replace("_nearNom", "")
    parts = name.split("@")[1].split("_")
    return int(parts[2]), int(parts[4])  # muE, muT


def get_results():
    results = []

    for fitdir in fitdirs():
        muE, muT = parse_fitdir(fitdir)
        fname = os.path.join(fitdir, "fit_shape_2d.root")
        s2t_result, dm2_result = read_fit_file(fname)
        s_min, s_best, s_max = s2t_result
        d_min, d_best, d_max = dm2_result
        results.append((muE, muT, s_best, s_min, s_max, d_best, d_min, d_max))

    return results


def dump_results():
    print("muE muT s_best s_min s_max d_best d_min d_max")

    for row in sorted(get_results()):
        print(' '.join(str(v) for v in row))


if __name__ == '__main__':
    dump_results()
