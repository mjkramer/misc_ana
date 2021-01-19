from glob import glob
import os

import pandas as pd
import ROOT as R

from plot_fit_results import read_study


def keep(o):
    R.SetOwnership(o, False)     # don't delete it, python!
    try:
        o.SetDirectory(R.gROOT)  # don't delete it, root!
        # o.SetDirectory(0)
    except Exception:
        pass                     # unless you weren't going to anyway
    return o


def dump_fit_results(study):
    df = read_study(study)
    df.to_csv(f"summaries/{study}.csv")


__T13_ROWS = {
    1: "obs_evt",
    2: "livetime",
    3: "veto_eff",
    4: "mult_eff",
    5: "delcut_eff",
    6: "power_unc",
    7: "tot_eff_unc",
    8: "target_mass",
    9: "tot_bkg",
    10: "tot_bkg_unc",
    11: "acc_bkg",
    12: "acc_bkg_unc",
    13: "li9_bkg",
    14: "li9_bkg_unc",
    15: "fastn_bkg",
    16: "fastn_bkg_unc",
    17: "amc_bkg",
    18: "amc_bkg_unc",
    19: "alphan_bkg",
    20: "alphan_bkg_unc"
}


def read_theta13_file(fname):
    "Returns {rowname: [valEH1AD1, ..., valEH3AD4]}"
    result = {}
    headers_remaining = 3

    for line in open(fname):
        line = line.strip()

        if line.startswith("#") or not line:
            continue

        if headers_remaining > 0:
            headers_remaining -= 1
            continue

        words = line.split()
        rownum = int(words[1])
        if rownum == 0:         # timestamps etc
            continue
        vals = map(float, words[2:])
        result[__T13_ROWS[rownum]] = list(vals)

    return result


def read_ibdsel_config(fname):
    results = {}
    for line in open(fname):
        if line.strip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        key, valstr = parts[:2]
        try:
            val = int(valstr)
        except ValueError:
            try:
                val = float(valstr)
            except ValueError:
                val = valstr
        results[key] = val
    return results
