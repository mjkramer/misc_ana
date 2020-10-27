#!/usr/bin/env python3

import argparse
import os

import pandas as pd
import numpy as np
from scipy.interpolate import interp2d

import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
for lib in ["common.so", "stage2.so"]:  # for Li9Calc
    R.gSystem.Load(os.path.join(os.getenv("IBDSEL_HOME"),
                                f"selector/_build/{lib}"))


class VetoEff:
    def __init__(self, nADs):
        self.dfs = {}
        for site in [1, 2, 3]:
            fname = f"output/vetoEff_pbp_eh{site}_{nADs}ad.txt"
            self.dfs[site] = pd.read_csv(fname, sep=r"\s+")

    def veto_eff(self, cut_pe, time_s, site, det):
        df = self.dfs[site]
        f = interp2d(df["cut_pe"], df["time_s"], df[f"effAD{det}"])
        return f(cut_pe, time_s)[0]


def det_active(nADs, site, det):
    if nADs == 6:
        return ((site == 1 and det in [1, 2]) or
                (site == 2 and det in [1]) or
                (site == 3 and det in [1, 2, 3]))
    if nADs == 8:
        return ((site == 1 and det in [1, 2]) or
                (site == 2 and det in [1, 2]) or
                (site == 3 and det in [1, 2, 3, 4]))
    if nADs == 7:
        return ((site == 1 and det in [1]) or
                (site == 2 and det in [1, 2]) or
                (site == 3 and det in [1, 2, 3, 4]))
    raise


def idet(site, det):
    return (site-1)*2 + (det-1)


def dets_for(site):
    if site not in [1, 2, 3]:
        raise
    return [1, 2, 3, 4] if site == 3 else [1, 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("outfile")
    ap.add_argument("nADs", type=int)
    ap.add_argument("cut_pe", type=float)
    ap.add_argument("time_s", type=float)
    args = ap.parse_args()

    f_in = open(args.template)
    f_out = open(args.outfile, "w")
    eff_calc = VetoEff(args.nADs)
    li9_calc = R.Li9Calc()

    out_lines = []
    line_indices = {}
    headers_remaining = 3

    for line in f_in:
        out_lines.append(line)

        if line.strip().startswith("#"):
            continue

        if headers_remaining > 0:
            headers_remaining -= 1
            continue

        words = line.strip().split()
        rownum = int(words[1])
        line_indices[rownum] = len(out_lines) - 1

    def get_vals(rownum, typ):
        lineno = line_indices[rownum]
        return [typ(w) for w in
                out_lines[lineno].split()[2:]]

    nom_obs_evts = get_vals(1, int)
    nom_veto_effs = get_vals(3, float)
    nom_li9_rates = get_vals(13, float)
    nom_li9_errs = get_vals(14, float)
    nom_bkg_rates = get_vals(9, float)
    nom_bkg_errs = get_vals(10, float)

    def new_vals(func):
        result = []
        for site in [1, 2, 3]:
            for det in dets_for(site):
                if det_active(args.nADs, site, det):
                    result.append(func(site, det))
                else:
                    result.append(0)
        return result

    def veto_eff(site, det):
        return eff_calc.veto_eff(args.cut_pe, args.time_s, site, det)
    veto_effs = new_vals(veto_eff)

    def obs_evt(site, det):
        i = idet(site, det)
        return nom_obs_evts[i] * veto_effs[i] / nom_veto_effs[i]
    obs_evts = new_vals(obs_evt)

    def li9_rate(site, _det):
        return li9_calc.li9daily_linreg(site, args.cut_pe, 1e3 * args.time_s)
    li9_rates = new_vals(li9_rate)

    def li9_err(site, det):
        i = idet(site, det)
        return nom_li9_errs[i] * li9_rates[i] / nom_li9_rates[i]
    li9_errs = new_vals(li9_err)

    def bkg_rate(site, det):
        i = idet(site, det)
        return nom_bkg_rates[i] - nom_li9_rates[i] + li9_rates[i]
    bkg_rates = new_vals(bkg_rate)

    def bkg_err(site, det):
        i = idet(site, det)
        return np.sqrt(nom_bkg_errs[i]**2
                       - nom_li9_errs[i]**2 + li9_errs[i]**2)
    bkg_errs = new_vals(bkg_err)

    def replace_line(rownum, vals, fmt="%f"):
        i = line_indices[rownum]
        part1 = " ".join(out_lines[i].split()[:2])
        part2 = " ".join(fmt % v for v in vals)
        out_lines[i] = f"{part1} {part2}\n"

    replace_line(1, obs_evts, "%d")
    replace_line(3, veto_effs, "%.4f")
    replace_line(13, li9_rates, "%.3f")
    replace_line(14, li9_errs, "%.4f")
    replace_line(9, bkg_rates, "%.4f")
    replace_line(10, bkg_errs, "%.5f")

    for line in out_lines:
        f_out.write(line)

    f_out.close()


if __name__ == '__main__':
    main()
