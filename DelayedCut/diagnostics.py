from functools import lru_cache
from glob import glob
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sys.path += [os.getenv("IBDSEL_HOME") + "/fit_prep"]
from delayed_eff import DelayedEffCalc

from util import read_theta13_file


def theta13_to_df(t13_file):
    data = read_theta13_file(t13_file)
    return pd.DataFrame(data=data, index=range(1, 9))


@lru_cache()
def dataframes():
    "Returns {4.0: {6: df, 8: df, 7: df}, ...}"
    result = {}
    basedir = "fit_results/delcut_first"
    for direc in sorted(glob(f"{basedir}/*MeV")):
        mev = float(os.path.basename(direc)[:-3])
        result[mev] = {}
        for nADs in [6, 8, 7]:
            t13_file = f"{direc}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
            result[mev][nADs] = theta13_to_df(t13_file)
    return result


def get_column(colname, dets, weight=True):
    dfs = dataframes()
    xs = list(dfs.keys())
    ys = []

    for mev in xs:
        y = 0
        tot_livetime = 0
        for nADs in [6, 8, 7]:
            for det in dets:
                vals = dfs[mev][nADs].loc[det]
                if weight:
                    y += vals["livetime"] * vals[colname]
                else:
                    y += vals[colname]
                tot_livetime += vals["livetime"]
        if weight:
            y /= tot_livetime
        ys.append(y)

    return np.array(xs), np.array(ys)


def plot_column(colname, dets, weight=True):
    xs, ys = get_column(colname, dets, weight)
    plt.figure()
    ret = plt.plot(xs, ys, 'o')
    plt.title(f"{colname} [{', '.join(map(str, dets))}]")

    return ret


def detno2sitedet(detno):
    site = [1, 1, 2, 2, 3, 3, 3, 3][detno-1]
    det = [1, 2, 1, 2, 1, 2, 3, 4][detno-1]
    return site, det


def plot_scale_factor(dets):
    dfs = dataframes()
    xs, ys = [], []
    home = os.getenv("IBDSEL_HOME")
    confdir = f"{home}/../data/config_sets/delcut_first"
    for conffile in glob(f"{confdir}/config.*.txt"):
        parts = os.path.basename(conffile).split(".")
        name = '.'.join(parts[1:-1])  # strip 'config.' and '.txt'
        mev = float(name.split("_")[-1][:-3])
        calc = DelayedEffCalc(conffile)
        y, tot_livetime = 0, 0

        for detno in dets:
            site, det = detno2sitedet(detno)
            for phase in [1, 2, 3]:
                nADs = [6, 8, 7][phase-1]
                livetime = dfs[mev][nADs].loc[detno]["livetime"]
                if livetime == 0:
                    continue
                factor = calc.scale_factor(phase, site, det)
                y += factor * livetime
                tot_livetime += livetime
        y /= tot_livetime

        xs.append(mev)
        ys.append(y)

    plt.plot(xs, ys, 'o')
    return xs, ys
