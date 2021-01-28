from functools import lru_cache
from glob import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import uproot

sys.path += [os.getenv("IBDSEL_HOME") + "/fit_prep"]
from delayed_eff import DelayedEffCalc

from util import read_theta13_file


def theta13_to_df(t13_file):
    data = read_theta13_file(t13_file)
    return pd.DataFrame(data=data, index=range(1, 9))


@lru_cache()
def dataframes(study="delcut_firstPlusFine"):
    "Returns {4.0: {6: df, 8: df, 7: df}, ...}"
    result = {}
    basedir = f"fit_results/{study}"
    for direc in sorted(glob(f"{basedir}/*MeV")):
        mev = float(os.path.basename(direc)[:-3])
        result[mev] = {}
        for nADs in [6, 8, 7]:
            t13_file = f"{direc}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
            result[mev][nADs] = theta13_to_df(t13_file)
    return result


def get_specint(dets, study="delcut_firstPlusFine"):
    dfs = dataframes(study=study)
    xs = list(dfs.keys())
    ys = []

    for mev in xs:
        y = 0
        for nADs in [6, 8, 7]:
            f = uproot.open(f"fit_results/{study}/{mev:.3f}MeV/" +
                            f"ibd_eprompt_shapes_{nADs}ad.root")
            for detno in dets:
                hall = [1, 1, 2, 2, 3, 3, 3, 3][detno - 1]
                det = [1, 2, 1, 2, 1, 2, 3, 4][detno - 1]
                h = f[f"h_ibd_eprompt_inclusive_eh{hall}_ad{det}"]
                y += sum(h)
        ys.append(y)

    return np.array(xs), np.array(ys)


def get_column(colname, dets, weight=True, study="delcut_firstPlusFine"):
    if colname == "specint":
        return get_specint(dets, study=study)

    dfs = dataframes(study=study)
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


def get_scale_factor(dets):
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

    return np.array(xs), np.array(ys)


def plot_scale_factor(dets):
    xs, ys = get_scale_factor(dets)
    return plt.plot(xs, ys, 'o')


def plot_scale_factor_nearfar():
    xs, ys_near = get_scale_factor([1, 2, 3, 4])
    _, ys_far = get_scale_factor([5, 6, 7, 8])
    plt.plot(xs, ys_far / ys_near, "o")
    plt.title("Delayed cut eff (rel to 6 MeV), far/near ratio")
    plt.xlabel("Delayed cut [MeV]")
    plt.savefig("gfx/nearfar.png")
