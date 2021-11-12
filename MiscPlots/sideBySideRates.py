#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

np.seterr(divide="ignore", invalid="ignore")


FILES = ["/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/fit_input/2021_02_03@delcut_fourth@flat@none_6.000MeV/Theta13-inputs_P17B_inclusive_6ad.txt",
         "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/fit_input/2021_02_03@delcut_fourth@flat@none_6.000MeV/Theta13-inputs_P17B_inclusive_8ad.txt",
         "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/fit_input/2021_02_03@delcut_fourth@flat@none_6.000MeV/Theta13-inputs_P17B_inclusive_7ad.txt",
         "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/fit_input/post17_v5v3v1@nominal/Theta13-inputs_P17B_inclusive_7ad.txt"
         ]

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
        result[__T13_ROWS[rownum]] = np.array(list(vals))

    return result


def rates_and_livetimes(t13file):
    d = read_theta13_file(t13file)

    rates = 1 / d['livetime'] \
        * ((d['obs_evt'] / d['veto_eff'] / d['mult_eff']) - d['tot_bkg'])

    errs = 1 / d['livetime'] \
        * np.sqrt(d['obs_evt'] / ((d['veto_eff'] * d['mult_eff']) ** 2) \
                  + (d['tot_bkg_unc'] ** 2))

    np.nan_to_num(rates, copy=False)
    np.nan_to_num(errs, copy=False)

    return rates, errs, d['livetime']


def summed_rates(file_indices):
    vals = [rates_and_livetimes(FILES[i]) for i in file_indices]
    allrates = [v[0] for v in vals]
    allerrs = [v[1] for v in vals]
    alltimes = [v[2] for v in vals]

    rates = sum([r * t for r, t in zip(allrates, alltimes)]) / sum(alltimes)
    errs = np.sqrt(sum([(e * t) ** 2 for e, t in zip(allerrs, alltimes)])) / sum(alltimes)

    # Keep NaNs so we don't plot points at zero
    # np.nan_to_num(rates, copy=False)
    # np.nan_to_num(errs, copy=False)

    return rates, errs


def plot_rates(file_indices, title):
    ys, yerr = summed_rates(file_indices)
    xs = range(1, 9)

    fig, ax = plt.subplots()
    ax.errorbar(xs, ys, yerr=yerr, fmt='o')
    ax.set_xlim(0.5, 8.5)
    ax.axvline(2.5, linestyle="--", color="black")
    ax.axvline(4.5, linestyle="--", color="black")

    ax.set_title(f"Daily IBD rates ({title})")
    ax.set_xlabel("AD [EH1, EH2, EH3]")

    fig.tight_layout()

    return fig, ax


def plot_rates_over_avg(file_indices, title):
    ys, yerr = summed_rates(file_indices)
    xs = range(1, 9)

    fig, ax = plt.subplots()
    ax.errorbar(xs, ys, yerr=yerr, fmt='o')
    ax.set_xlim(0.5, 8.5)
    ax.axvline(2.5, linestyle="--", color="black")
    ax.axvline(4.5, linestyle="--", color="black")

    ax.set_title(f"Daily IBD rates ({title})")
    ax.set_xlabel("AD [EH1, EH2, EH3]")

    fig.tight_layout()

    return fig, ax
