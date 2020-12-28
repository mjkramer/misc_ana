from glob import glob
import os

import pandas as pd
import ROOT as R

from plot_fit_results import read_study


T13_ROWS = {
    "obs_evt": 1,
    "livetime": 2,
    "veto_eff": 3,
    "mult_eff": 4,
    "delcut_eff": 5,
    "power_unc": 6,
    "tot_eff_unc": 7,
    "target_mass": 8,
    "tot_bkg": 9,
    "tot_bkg_unc": 10,
    "acc_bkg": 11,
    "acc_bkg_unc": 12,
    "li9_bkg": 13,
    "li9_bkg_unc": 14,
    "fastn_bkg": 15,
    "fastn_bkg_unc": 16,
    "amc_bkg": 17,
    "amc_bkg_unc": 18,
    "alphan_bkg": 19,
    "alphan_bkg_unc": 20
}


def read_theta13_file(fname):
    "Returns {rownum: [valAD1, ..., valAD8]}"
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
        result[rownum] = list(vals)

    return result


def dump_quantity(study, rowname, nADs=8):
    data = []

    for direc in glob(f"fit_results/{study}/*"):
        parts = os.path.basename(direc).split("_")
        cut_pe = float(parts[-2][:-2])
        time_s = float(parts[-1][:-1])

        t13_file = f"{direc}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        t13_data = read_theta13_file(t13_file)
        t13_row = t13_data[T13_ROWS[rowname]]
        vals = {f"AD{i+1}": t13_row[i] for i in range(8)}
        row = {"cut_pe": cut_pe, "time_s": time_s, **vals}
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(f"summaries/{study}.{rowname}.{nADs}ad.csv")


def dump_spectra_integrals(study, nADs=8):
    data = []

    for direc in glob(f"fit_results/{study}/*"):
        parts = os.path.basename(direc).split("_")
        cut_pe = float(parts[-2][:-2])
        time_s = float(parts[-1][:-1])

        spec_file = R.TFile(f"{direc}/ibd_eprompt_shapes_{nADs}ad.root")
        halls = [1, 1, 2, 2, 3, 3, 3, 3]
        dets = [1, 2, 1, 2, 1, 2, 3, 4]
        vals = {}
        for idet in range(8):
            hname = f"h_ibd_eprompt_inclusive_eh{halls[idet]}_ad{dets[idet]}"
            h = spec_file.Get(hname)
            vals[f"AD{idet+1}"] = h.Integral()
        row = {"cut_pe": cut_pe, "time_s": time_s, **vals}
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(f"summaries/{study}.spec_int.{nADs}ad.csv")


def dump_fit_results(study):
    df = read_study(study)
    df.to_csv(f"summaries/{study}.csv")
