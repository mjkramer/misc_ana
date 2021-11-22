from dataclasses import dataclass, asdict
from functools import lru_cache
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

SUFFIX = ""                     # at end of plot title

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


def read_study(study, numerical=True):
    data = []
    for direc in sorted(glob(f"fit_results/{study}/*")):
        print(direc)
        fit_result = read_fit_file(f"{direc}/fit_shape_2d.root")
        if numerical:
            parts = direc.split("/")[-1].split("_")
            cut_mev = float(parts[-1][:-3])
            ident = {"cut_mev": cut_mev}
        else:
            ident = {"ident": os.path.basename(direc)}
        data.append({**ident, **asdict(fit_result)})
    return pd.DataFrame(data)


def read_csv(csvfile):
    "Reads what we get from df.to_csv(csvfile)"
    df = pd.read_csv(csvfile, index_col=0)
    for qty in ["s2t", "dm2"]:
        df[f"{qty}_mid"] = (df[f"{qty}_min1sigma"] + df[f"{qty}_max1sigma"]) / 2
    return df


def plot_fit(studies,
             qty="s2t", title=r"$\sin^2 2\theta_{13}$ (best fit)",
             best_or_mid="best",
             labels=None):
    if type(studies) is str:
        studies = [studies]
    if labels is None:
        labels = studies

    fig, ax = plt.subplots()

    for study, label in zip(studies, labels):
        df = read_csv(f"summaries/{study}.csv")
        xs = df["cut_mev"]
        ymin = df[f"{qty}_min1sigma"]
        ymax = df[f"{qty}_max1sigma"]

        if best_or_mid == "best":
            ys = df[f"{qty}_best"]
        else:
            ys = (ymin + ymax) / 2

        yerrlow = ys - ymin
        yerrhigh = ymax - ys

        ax.errorbar(xs, ys, yerr=[yerrlow, yerrhigh], fmt="o",
                    label=label)

    ax.set_title(title + SUFFIX)
    ax.set_xlabel("Minimum delayed energy (MeV)")
    ax.set_ylabel(r"$\sin^2 2\theta_{13}$" if qty == "s2t"
                  else r"$\Delta m^2_{ee}$")
    if len(studies) > 1:
    # if True:
        ax.legend()
    fig.tight_layout()

    studyname = "+".join(studies)
    outdir = f"gfx/fit_results/{studyname}"
    filename = f"{qty}_{best_or_mid}.pdf"
    os.system(f"mkdir -p {outdir}")
    fig.savefig(f"{outdir}/{filename}")


def plot_s2t_best(studies, **kw):
    # plot_fit(studies, "s2t", r"$\sin^2 2\theta_{13}$ (best fit)", "best", **kw)
    plot_fit(studies, "s2t", r"$\sin^2 2\theta_{13}$ vs. minimum delayed energy", "best", **kw)


def plot_s2t_mid(studies, **kw):
    # plot_fit(studies, "s2t", r"$\sin^2 2\theta_{13}$ (1$\sigma$ midpoint)", "mid", **kw)
    plot_fit(studies, "s2t", r"$\sin^2 2\theta_{13}$ vs. minimum delayed energy", "mid", **kw)


def plot_dm2_best(studies, **kw):
    # plot_fit(studies, "dm2", r"$\Delta m^2_{ee}$ (best fit)", "best", **kw)
    plot_fit(studies, "dm2", r"$\Delta m^2_{ee}$ vs. minimum delayed energy", "best", **kw)


def plot_dm2_mid(studies, **kw):
    # plot_fit(studies, "dm2", r"$\Delta m^2_{ee}$ (1$\sigma$ midpoint)", "mid", **kw)
    plot_fit(studies, "dm2", r"$\Delta m^2_{ee}$ vs. minimum delayed energy", "mid", **kw)


def plot_fit_all(studies, **kw):
    plot_s2t_best(studies)
    plot_s2t_mid(studies)
    plot_dm2_best(studies)
    plot_dm2_mid(studies)


def plot_fit_unc(studies, qty, title, labels=None, **kw):
    if type(studies) is str:
        studies = [studies]
    if labels is None:
        labels = studies

    fig, ax = plt.subplots()

    for study, label in zip(studies, labels):
        df = read_csv(f"summaries/{study}.csv")
        xs = df["cut_mev"]
        ymin = df[f"{qty}_min1sigma"]
        ymax = df[f"{qty}_max1sigma"]

        ax.scatter(xs, (ymax - ymin) / 2, label=label)

    ax.set_title(title)
    ax.set_xlabel("Minimum delayed energy (MeV)")
    ax.set_ylabel(r"Error in $\sin^2 2\theta_{13}$" if qty == "s2t"
                  else r"Error in $\Delta m^2_{ee}$")
    if len(studies) > 1:
    # if True:
        ax.legend()
    fig.tight_layout()

    studyname = "+".join(studies)
    outdir = f"gfx/fit_unc/{studyname}"
    filename = f"unc_{qty}.pdf"
    os.system(f"mkdir -p {outdir}")
    fig.savefig(f"{outdir}/{filename}")


def plot_s2t_unc(studies, **kw):
    plot_fit_unc(studies, "s2t", r"$\sin^2 2\theta_{13}$ uncertainty vs. minimum delayed energy", **kw)


def plot_dm2_unc(studies, **kw):
    plot_fit_unc(studies, "dm2", r"$\Delta m^2_{ee}$ uncertainty vs. minimum delayed energy", **kw)


def plot_fit_unc_all(studies, **kw):
    plot_s2t_unc(studies, **kw)
    plot_dm2_unc(studies, **kw)


def plot_methcomp():
    studies = ["delcut_fourth@bcw@flat@none@@redo",
               "delcut_fourth@bcw@rel@old@@redo", "delcut_fourth@bcw@rel@new@@redo",
               "delcut_fourth@bcw@abs@old@@redo", "delcut_fourth@bcw@abs@new@@redo"]
    labels = ["Flat", "Rel + old", "Rel + new", "Abs + old", "Abs + new"]
    plot_s2t_best(studies, labels=labels)
    plot_dm2_best(studies, labels=labels)
    plot_s2t_mid(studies, labels=labels)
    plot_dm2_mid(studies, labels=labels)


def plot_fit_unc_thesis():
    studies = ["delcut_fourth@bcw@rel@new@@redo",
               "delcut_fourth_toymc@bcw@@redo"]
    labels = ["Data", "Toy MC"]
    plot_fit_unc_all(studies, labels=labels)

def plot_bincomp():
    studies = ["delcut_fourth@bcw@rel@new@@redo",
               "delcut_fourth@lbnl@rel@new@@redo"]
    labels = ["BCW binning", "LBNL binning",]
    plot_s2t_best(studies, labels=labels)
    plot_dm2_best(studies, labels=labels)
    plot_s2t_mid(studies, labels=labels)
    plot_dm2_mid(studies, labels=labels)

def plot_vtxcomp_thesis_old():
    studies = ["delcut_fourth",
               "newVtxEff2_rInside1000", "newVtxEff2_rOutside1000",
               "newVtxEff2_zBotThird", "newVtxEff2_zMidThird",
               "newVtxEff2_zTopThird"]
    labels = ["Full", "Inside", "Outside", "Bottom", "Middle", "Top"]
    plot_s2t_mid(studies, labels=labels)
    plot_dm2_mid(studies, labels=labels)

def plot_vtxcomp_thesis():
    studies = ["delcut_fourth@bcw@rel@new@@redo",
               "newVtxEff2_rInside1000@bcw@@redo", "newVtxEff2_rOutside1000@bcw@@redo",
               "newVtxEff2_zBotThird@bcw@@redo", "newVtxEff2_zMidThird@bcw@@redo",
               "newVtxEff2_zTopThird@bcw@@redo"]
    labels = ["Full", "Inside", "Outside", "Bottom", "Middle", "Top"]
    plot_s2t_best(studies, labels=labels)
    plot_dm2_best(studies, labels=labels)
    plot_s2t_mid(studies, labels=labels)
    plot_dm2_mid(studies, labels=labels)
