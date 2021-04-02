from dataclasses import dataclass, asdict
from glob import glob
import os

import numpy as np
import ROOT as R
import pandas as pd


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
        return ((yval - ys[i + 1]) * xs[i] + (ys[i] - yval) * xs[i + 1]) / \
            (ys[i] - ys[i + 1])

    xmin, xmax = xs[0], xs[-1]

    for i in range(len(ys) - 1):
        if ys[i] > yval and ys[i + 1] <= yval:
            xmin = interp(i)
        elif ys[i] <= yval and ys[i + 1] > yval:
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

    chi2_map = [[h.GetBinContent(is2 + 1, idm + 1) for is2 in range(nS2T)]
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
    for direc in sorted(glob(f"data/fit_results/{study}/*")):
        print(direc)
        fit_result = read_fit_file(f"{direc}/fit_shape_2d.root")
        title = {"title": os.path.basename(direc)}
        data.append({**title, **asdict(fit_result)})
    return pd.DataFrame(data)


def read_csv(csvfile):
    "Reads what we get from df.to_csv(csvfile)"
    return pd.read_csv(csvfile, index_col=0)


def dump_fit_results(study, **kw):
    os.system("mkdir -p data/summaries")
    df = read_study(study, **kw)
    df.to_csv(f"data/summaries/{study}.csv")
