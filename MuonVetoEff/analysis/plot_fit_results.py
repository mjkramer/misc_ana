from dataclasses import dataclass, asdict
from glob import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import ROOT as R
import pandas as pd

try:
    from mplhacks import mplhacks
    mplhacks()
except Exception:
    pass


@dataclass
class FitResult:
    s2t_best: float
    s2t_min1sigma: float
    s2t_max1sigma: float

    dm2_best: float
    dm2_min1sigma: float
    dm2_max1sigma: float


def find_lims(xs, ys, yval):
    """ Interpolate the x positions where y crosses yval. Assumes ys is concave
    up. """
    assert len(xs) == len(ys)

    def interp(i):
        return ((yval - ys[i+1]) * xs[i] + (ys[i] - yval) * xs[i+1]) / \
            (ys[i] - ys[i+1])

    xmin, xmax = xs[0], xs[-1]

    for i in range(len(ys) - 1):
        if ys[i] > yval and ys[i+1] <= yval:
            xmin = interp(i)
        elif ys[i] <= yval and ys[i+1] > yval:
            xmax = interp(i)
            break

    if xmin == xs[0]:
        print("Warning: Default xmin")
    if xmax == xs[-1]:
        print("Warning: Default xmax")

    return xmin, xmax


def read_fit_file(fname):
    f = R.TFile(fname)
    h = f.h_chi2_map

    # XXX keep this or not?
    t = f.Get("tr_fit")
    t.GetEntry(0)
    s2t_best = t.GetLeaf("s2t_min").GetValue()
    dm2_best = t.GetLeaf("dm2_min").GetValue()

    # NB: This is valid for fit results generated after Oct 27 2020
    # For older results, need (GetBinLowEdge(1), GetBinUpEdge(N))
    nS2T = h.GetNbinsX()
    nDM2 = h.GetNbinsY()
    s2t_min = h.GetXaxis().GetBinCenter(1)
    s2t_max = h.GetXaxis().GetBinCenter(nS2T)
    dm2_min = h.GetYaxis().GetBinCenter(1)
    dm2_max = h.GetYaxis().GetBinCenter(nDM2)

    chi2_map = [[h.GetBinContent(is2+1, idm+1) for is2 in range(nS2T)]
                for idm in range(nDM2)]
    chi2_map = np.array(chi2_map)

    chi2_best = chi2_map.min()

    sin22t13 = np.linspace(s2t_min, s2t_max, nS2T)
    dm2 = np.linspace(dm2_min, dm2_max, nDM2)

    def get_dChi2_s2t(is2):
        proj_chi2 = 1e10
        for idm in range(nDM2):
            if chi2_map[idm][is2] < proj_chi2:
                proj_chi2 = chi2_map[idm][is2]
        return proj_chi2 - chi2_best

    def get_dChi2_dm2(idm):
        proj_chi2 = 1e10
        for is2 in range(nS2T):
            if chi2_map[idm][is2] < proj_chi2:
                proj_chi2 = chi2_map[idm][is2]
        return proj_chi2 - chi2_best

    chi2_s2t = np.array([get_dChi2_s2t(is2) for is2 in range(nS2T)])
    chi2_dm2 = np.array([get_dChi2_dm2(idm) for idm in range(nDM2)])

    s2t_min1sigma, s2t_max1sigma = find_lims(sin22t13, chi2_s2t, 1)
    dm2_min1sigma, dm2_max1sigma = find_lims(dm2, chi2_dm2, 1)

    return FitResult(s2t_best=s2t_best,
                     s2t_min1sigma=s2t_min1sigma,
                     s2t_max1sigma=s2t_max1sigma,
                     dm2_best=dm2_best,
                     dm2_min1sigma=dm2_min1sigma,
                     dm2_max1sigma=dm2_max1sigma)


def read_study(study):
    data = []
    for direc in sorted(glob(f"fit_results/{study}/*")):
        print(direc)
        parts = direc.split("/")[-1].split("_")
        cut_pe = float(parts[-2][:-2])
        time_s = float(parts[-1][:-1])
        fit_result = read_fit_file(f"{direc}/fit_shape_2d.root")
        row = {'cut_pe': cut_pe, 'time_s': time_s, **asdict(fit_result)}
        data.append(row)
    return pd.DataFrame(data)


def read_study_csv(csvfile):
    "Reads what we get from df.to_csv(csvfile)"
    return pd.read_csv(csvfile, index_col=0)


# https://stackoverflow.com/questions/43525546/plotting-pcolormesh-from-filtered-pandas-dataframe-for-defined-x-y-ranges-even
def plot2d(df, expr, title, name, tag):
    df = df.copy()
    df["vals"] = df.eval(expr)
    piv = df.pivot_table(index="time_s", columns="cut_pe", values="vals")
    print(piv)

    # plt.figure(figsize=[9.6, 7.2])
    plt.figure()
    plt.pcolormesh(piv.columns, piv.index, piv.values,
                   shading="nearest")
    plt.colorbar()
    plt.title(title)
    plt.xlabel("Shower muon definition [pe]")
    plt.ylabel("Shower veto time [s]")
    plt.xticks(piv.columns)
    plt.yticks(piv.index)
    plt.tight_layout()

    fname = f"gfx/{tag}/{name}.pdf"
    os.system(f"mkdir -p {os.path.dirname(fname)}")
    plt.savefig(fname)


def plot_s2t_best(df, tag):
    return plot2d(df, "s2t_best", r"Best fit $\sin^2 2\theta_{13}$",
                  "s2t_best", tag)


def plot_dm2_best(df, tag):
    return plot2d(df, "dm2_best", r"Best fit $\Delta m^2_{ee}$",
                  "dm2_best", tag)


def plot_s2t_mid(df, tag):
    return plot2d(df, "0.5 * (s2t_max1sigma + s2t_min1sigma)",
                  r"Middle of 1$\sigma$ range for $\sin^2 2\theta_{13}$",
                  "s2t_mid", tag)


def plot_dm2_mid(df, tag):
    return plot2d(df, "0.5 * (dm2_max1sigma + dm2_min1sigma)",
                  r"Middle of 1$\sigma$ range for $\Delta m^2_{ee}$",
                  "dm2_mid", tag)


def plot_s2t_unc(df, tag):
    return plot2d(df, "0.5 * (s2t_max1sigma - s2t_min1sigma)",
                  r"1$\sigma$ uncertainty on $\sin^2 2\theta_{13}$",
                  "s2t_unc", tag)


def plot_dm2_unc(df, tag):
    return plot2d(df, "0.5 * (dm2_max1sigma - dm2_min1sigma)",
                  r"1$\sigma$ uncertainty on $\Delta m^2_{ee}$",
                  "dm2_unc", tag)


def plot_all(tag):
    df = read_study_csv(f"summaries/{tag}.csv")
    # plot_s2t_best(df, tag)
    # plot_dm2_best(df, tag)
    # plot_s2t_unc(df, tag)
    # plot_dm2_unc(df, tag)
    plot_s2t_mid(df, tag)
    plot_dm2_mid(df, tag)


def plot_all_all():
    for tag in ["oct20_data_bcw", "oct20_data", "oct20_yolo3_bcw",
                "oct20_yolo3_truePars_bcw", "oct20_yolo3_truePars"]:
        plot_all(tag)
