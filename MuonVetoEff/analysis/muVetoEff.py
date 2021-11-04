import os
import ROOT as R
R.gROOT.SetBatch(True)
if os.getenv("IBDSEL_HOME"):
    for lib in ["common.so", "stage2.so"]:
        R.gSystem.Load(os.path.join(os.getenv("IBDSEL_HOME"), f"selector/_build/{lib}"))
R.gROOT.ProcessLine(f".L {os.path.dirname(__file__)}/../toymc/muveto_toy.cc+")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from root_pandas import read_root
from scipy import stats
from functools import lru_cache

try:
    import mplhacks
except:
    pass

# shower muon PE
# CUTS = np.arange(1.8e5, 5.001e5, 0.1e5)
CUTS = np.arange(1.8e5, 4.40001e5, 0.2e5)
TIMES = np.arange(0.250, 1.8750001, 0.125)


@lru_cache()
def tfile(site):
    return R.TFile(f"muons.dbd.eh{site}.0001.root")


def vetoEff(f, det, showerCut, showerTime):
    livetime = f.h_livetime.GetBinContent(1)
    h_wp = f.Get(f"h_wpMuons_ad{det}")
    h_ad = f.Get(f"h_adMuons_ad{det}")

    n_wp = h_wp.Integral(h_wp.FindBin(13), h_wp.GetNbinsX())
    cutbin = h_ad.FindBin(showerCut)
    n_ad = h_ad.Integral(h_ad.FindBin(3000), cutbin - 1)
    n_sh = h_ad.Integral(cutbin, h_ad.GetNbinsX())

    toy = R.MuVetoToy()
    toy.tVetoSh = showerTime
    return toy.vetoEff(n_wp/livetime, n_ad/livetime, n_sh/livetime)

    # t_shVeto = n_sh * showerTime
    # t_adVeto = n_ad * 1_402e-6 * (1 - t_shVeto / livetime)
    # t_wpVeto = n_wp * 602e-6 * (1 - t_shVeto / livetime) * (1 - t_adVeto / livetime)
    # t_adVeto *= (1 - t_wpVeto / livetime)

    # t_shVeto = n_sh * showerTime
    # t_adVeto = n_ad * 1_402e-6
    # t_wpVeto = n_wp * 602e-6
    # t_adVeto *= (1 - t_wpVeto / livetime)

    # return 1 - (t_wpVeto + t_adVeto + t_shVeto) / livetime


def scale_unc(site, det, showerCut, showerTime):
    nomCut = 3e5
    nomTime = 0.4004

    li9_budget = 0.05           # doc-11724
    stat_budget = 0.55
    rest_budget = 1 - li9_budget - stat_budget

    calc = R.Li9Calc()

    eff = vetoEff(tfile(site), det, showerCut, showerTime)
    eff_nom = vetoEff(tfile(site), det, nomCut, nomTime)

    # rate = calc.li9daily_nearest(1, showerCut, 1e3 * showerTime)
    # rate_nom = calc.li9daily_nearest(1, nomCut, 1e3 * nomTime)

    # rate = li9_linreg(site, showerCut, showerTime)
    # rate_nom = li9_linreg(site, nomCut, nomTime)

    rate = calc.li9daily_linreg(site, showerCut, 1e3 * showerTime)
    rate_nom = calc.li9daily_linreg(site, nomCut, 1e3 * nomTime)

    new_unc = li9_budget * rate/rate_nom + stat_budget * np.sqrt(eff_nom/eff) + rest_budget
    return new_unc

def plot2d(func, fname, title, **kwargs):
    # times = np.arange(0.1, 2.01, 0.1)

    vals = [[func(cut, time) for cut in CUTS]
            for time in TIMES]

    plt.figure()
    plt.pcolormesh(CUTS, TIMES, vals, shading='nearest', **kwargs)
    plt.xticks(CUTS[::2])
    plt.yticks(TIMES)
    plt.plot(3e5, 0.375, "P", markerfacecolor="red", markeredgecolor="red", ms=8)
    plt.plot(4e5, 1, "X", markerfacecolor="darkorange", markeredgecolor="darkorange", ms=8)
    plt.colorbar()
    plt.title(title)
    plt.xlabel("Shower muon definition [p. e.]")
    plt.ylabel("Shower veto time [s]")
    plt.tight_layout()
    plt.savefig(f"gfx/{fname}.pdf")

def plot_vetoEff(site, det):
    def f(cut, time):
        return vetoEff(tfile(site), det, cut, time)
    return plot2d(f, f"vetoEff_eh{site}_ad{det}", f"Muon veto efficiency, EH{site}-AD{det}")

def plot_vetoEff_pbp_2d(nADs, site, det, **kwargs):
    df = pd.read_csv(f"output/vetoEff_pbp_eh{site}_{nADs}ad.txt",
                     sep=r"\s+")
    def f(cut, time):
        print(cut, time)
        # sub_df = df.query(f"cut_pe == {cut} and time_s == {time}")
        sub_df = df[np.isclose(df.cut_pe, cut)]
        sub_df = sub_df[np.isclose(sub_df.time_s, time)]
        return sub_df[f"effAD{det}"].iloc[0]
    return plot2d(f, f"vetoEff_pbp_2d_{nADs}ad_eh{site}_ad{det}",
                  f"Muon veto efficiency, EH{site}-AD{det}", **kwargs)


def plot_unc(site, det, **kwargs):
    def f(cut, time):
        return scale_unc(site, det, cut, time)
    return plot2d(f, f"theta13_unc_eh{site}_ad{det}", f"Theta13 uncertainty, EH{site}-AD{det}", **kwargs)

# def plot_li9_calc(site, mode=R.Li9Calc.Mode.Nominal):
#     calc = R.Li9Calc()
#     calc.setMode(mode)

#     def f(cut, time):
#         # return calc.li9daily_nearest(site, cut, 1e3 * time)
#         return calc.li9daily_linreg(site, cut, 1e3 * time)
#     return plot2d(f, f"li9_calc_eh{site}", f"Li9 daily rate (C++), EH{site}")

def plot_li9_linreg(site):
    def f(cut, time):
        return li9_linreg(site, cut, time)
    return plot2d(f, f"li9_linreg_eh{site}", f"Li9 rate (/AD/day), EH{site}")

# garbage
def li9_quick(site, cut, time_s):
    # At 2.5e5 and 3.5e5, for 0.4s veto
    intercepts = {1: (2.35, 2.85),
                  2: (1.35, 1.85),
                  3: (0.15, 0.2)}

    tau_s = 0.257                # Li9

    y1, y2 = intercepts[site]
    rate_for_400ms = y1 + (y2 - y1) / (3.5e5 - 2.5e5) * (cut - 2.5e5)
    return rate_for_400ms * np.exp(-time_s / tau_s) / np.exp(-0.4004 / tau_s)

def li9_linreg(site, cut, time_s):
    calc = R.Li9Calc()
    vals = []
    # for mode in range(4):
    for mode in range(1):
        calc.setMode(mode)
        vals += [calc.li9daily_nearest(site, cut, 1e3 * time_s)
                 for cut in CUTS]
    # xs = list(CUTS) * 4
    xs = list(CUTS)
    m, b, *_ = stats.linregress(xs, vals)
    return m * cut + b

# XXX for Kam-Biu
def plot_li9_1d(site, time=0.4004):
    calc = R.Li9Calc()

    plt.figure()

    # mode_names = ['Nominal', 'No B12', '15% He8', 'No He8']
    mode_names = ['Nominal']

    for mode, name in enumerate(mode_names):
        calc.setMode(mode)
        # vals = [calc.li9daily_nearest(site, cut, 1e3 * time)
        vals = [calc.li9daily_linreg(site, cut, 1e3 * time)
                for cut in CUTS]
        plt.plot(CUTS, vals, 'o', label=name)

    # quickvals = [li9_quick(site, cut, time) for cut in CUTS]
    # plt.plot(CUTS, quickvals)
    linregvals = [li9_linreg(site, cut, time) for cut in CUTS]
    plt.plot(CUTS, linregvals)

    plt.title(f"Daily Li9 rate, {time}s veto, EH{site}")
    plt.xlabel("Shower muon definition [p.e.]")

    # plt.legend()
    plt.tight_layout()
    plt.savefig(f"gfx/li9_1d_eh{site}_{int(time*1000)}ms.png")

def plot_vetoEff_dbd_validation(site, det):
    df_ibdsel = read_root([f"stage2_pbp/stage2.pbp.eh{site}.{N}ad.root"
                           for N in [6, 8, 7]],
                          "results")
    df_ibdsel = df_ibdsel.query(f"detector == {det} and vetoEff != 0")

    df_toy = pd.read_csv(f"output/vetoEff_dbd_eh{site}.txt", sep=r"\s+")
    df_toy = df_toy.query(f"effAD{det} != 0")

    plt.figure(figsize=[9.6, 7.2])
    plt.plot(df_ibdsel["seq"], df_ibdsel["vetoEff"], "o", label="From IBD selection")
    plt.plot(df_toy["day"], df_toy[f"effAD{det}"], "o", label="Independent calc")
    plt.legend()
    plt.title(f"Muon veto efficiency, nominal cuts, EH{site}-AD{det}")
    plt.xlabel("Day")
    plt.tight_layout()
