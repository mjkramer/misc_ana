#!/usr/bin/env python3

import argparse
from glob import glob
import os
import sys

import pandas as pd
import numpy as np
from scipy.interpolate import interp2d

import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
from root_pandas import read_root

for lib in ["common.so", "stage2.so"]:
    R.gSystem.Load(os.path.join(os.getenv("IBDSEL_HOME"),
                                f"selector/_build/{lib}"))

sys.path += [os.getenv("IBDSEL_HOME") + "/fit_prep"]
from delayed_eff import DelayedEffCalc

from util import keep, read_ibdsel_config


def make_singles_calc(nominal_ibdsel_config_file, stage2_file, det,
                      prompt_min, prompt_max,
                      delayed_min, delayed_max):
    config = read_ibdsel_config(nominal_ibdsel_config_file)
    f = R.TFile(stage2_file)
    df = read_root(stage2_file, "results")
    df = df.query(f"detector == {det}")

    hSing = keep(f.Get(f"h_single_AD{det}"))
    if not hSing:
        return None

    livetime_s = sum(df["livetime_s"])
    eMuIbd = sum(df["vetoEff"] * df["livetime_s"]) / livetime_s
    eMuSingles = sum(df["vetoEffSingles"] * df["livetime_s"]) / livetime_s

    singleMultCuts = R.MultCutTool.Cuts()
    singleMultCuts.usec_before = config["singleDmcUsecBefore"]
    singleMultCuts.emin_before = config["singleDmcEminBefore"]
    singleMultCuts.emax_before = config["singleDmcEmaxBefore"]
    singleMultCuts.usec_after = config["singleDmcUsecAfter"]
    singleMultCuts.emin_after = config["singleDmcEminAfter"]
    singleMultCuts.emax_after = config["singleDmcEmaxAfter"]

    ibdMultCuts = R.MultCutTool.Cuts()
    ibdMultCuts.usec_before = config["ibdDmcUsecBefore"]
    ibdMultCuts.emin_before = config["ibdDmcEminBefore"]
    ibdMultCuts.emax_before = config["ibdDmcEmaxBefore"]
    ibdMultCuts.usec_after = config["ibdDmcUsecAfter"]
    ibdMultCuts.emin_after = config["ibdDmcEminAfter"]
    ibdMultCuts.emax_after = config["ibdDmcEmaxAfter"]

    return R.SinglesCalc(hSing, eMuIbd, livetime_s,
                         singleMultCuts, ibdMultCuts, eMuSingles,
                         prompt_min, prompt_max,
                         delayed_min, delayed_max,
                         config["ibdDtMaxUsec"])


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
        return ((site == 1 and det in [2]) or
                (site == 2 and det in [1, 2]) or
                (site == 3 and det in [1, 2, 3, 4]))
    raise


def idet(site, det):
    return (site-1)*2 + (det-1)


def dets_for(site):
    if site not in [1, 2, 3]:
        raise
    return [1, 2, 3, 4] if site == 3 else [1, 2]


def find_stage2_file(template_fname, nADs, site):
    direc = os.path.dirname(template_fname)
    selname = os.path.basename(direc)
    return f"{direc}/../../stage2_pbp/{selname}/stage2.pbp.eh{site}.{nADs}ad.root"


def find_ibdsel_config(template_fname):
    direc = os.path.dirname(template_fname)
    selname = os.path.basename(direc)
    return glob(f"{direc}/../../stage2_pbp/{selname}/config.*.txt")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("outfile")
    ap.add_argument("nADs", type=int)
    ap.add_argument("--prompt-min", type=float, default=0.7)
    ap.add_argument("--prompt-max", type=float, default=12)
    ap.add_argument("--delayed-min", type=float, default=6)
    ap.add_argument("--delayed-max", type=float, default=12)
    args = ap.parse_args()

    f_in = open(args.template)
    f_out = open(args.outfile, "w")

    stage2_files = [find_stage2_file(args.template, args.nADs, site)
                    for site in [1, 2, 3]]
    nominal_ibdsel_config_file = find_ibdsel_config(args.template)
    singcalcs = [make_singles_calc(nominal_ibdsel_config_file,
                                   stage2_files[site-1], det,
                                   args.prompt_min, args.prompt_max,
                                   args.delayed_min, args.delayed_max)
                 for site in [1, 2, 3] for det in dets_for(site)]

    print(singcalcs)

    phase = {6: 1, 8: 2, 7: 3}[args.nADs]
    effcalc = DelayedEffCalc(nominal_ibdsel_config_file)
    effcalc.cut = args.delayed_min
    scale_factors = [1] * 8
    for site in [1, 2, 3]:
        for det in dets_for(site):
            if det_active(args.nADs, site, det):
                scale_factors[idet(site, det)] = \
                    effcalc.scale_factor(phase, site, det)

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
    veto_effs = get_vals(3, float)
    nom_dmc_effs = get_vals(4, float)
    nom_bkg_rates = get_vals(9, float)
    # nom_acc_rates = get_vals(11, float)
    # nom_acc_errs = get_vals(12, float)
    nom_li9_rates = get_vals(13, float)
    nom_li9_errs = get_vals(14, float)
    nom_fastn_rates = get_vals(15, float)
    nom_fastn_errs = get_vals(16, float)
    amc_rates = get_vals(17, float)
    amc_errs = get_vals(18, float)
    nom_alphan_rates = get_vals(19, float)
    nom_alphan_errs = get_vals(20, float)

    def new_vals(func):
        result = []
        for site in [1, 2, 3]:
            for det in dets_for(site):
                if det_active(args.nADs, site, det):
                    result.append(func(site, det))
                else:
                    result.append(0)
        return result

    def dmc_eff(site, det):
        i = idet(site, det)
        return singcalcs[i].dmcEff()
    dmc_effs = new_vals(dmc_eff)

    def acc_rate(site, det):
        i = idet(site, det)
        return singcalcs[i].accDaily()
    acc_rates = new_vals(acc_rate)

    def acc_err(site, det):
        i = idet(site, det)
        return singcalcs[i].accDailyErr(site)
    acc_errs = new_vals(acc_err)

    def li9_rate(site, _det):
        i = idet(site, det)
        return nom_li9_rates[i] * scale_factors[i]
    li9_rates = new_vals(li9_rate)

    def li9_err(site, _det):
        i = idet(site, det)
        return nom_li9_errs[i] * scale_factors[i]
    li9_errs = new_vals(li9_err)

    def fastn_rate(site, _det):
        i = idet(site, det)
        return nom_fastn_rates[i] * scale_factors[i]
    fastn_rates = new_vals(fastn_rate)

    def fastn_err(site, _det):
        i = idet(site, det)
        return nom_fastn_errs[i] * scale_factors[i]
    fastn_errs = new_vals(fastn_err)

    def alphan_rate(site, _det):
        i = idet(site, det)
        return nom_alphan_rates[i] * scale_factors[i]
    alphan_rates = new_vals(alphan_rate)

    def alphan_err(site, _det):
        i = idet(site, det)
        return nom_alphan_errs[i] * scale_factors[i]
    alphan_errs = new_vals(alphan_err)

    def bkg_rate(site, det):
        i = idet(site, det)
        return acc_rates[i] + li9_rates[i] + fastn_rates[i] + amc_rates[i] + \
            alphan_rates[i]
    bkg_rates = new_vals(bkg_rate)

    def bkg_err(site, det):
        i = idet(site, det)
        return np.sqrt(acc_errs[i]**2 + li9_errs[i]**2 + fastn_errs[i]**2 +
                       amc_errs[i]**2 + alphan_errs[i]**2)
    bkg_errs = new_vals(bkg_err)

    # XXX
    # this isn't actually used, but we show the calculation for reference
    def obs_evt(site, det):
        i = idet(site, det)
        return (nom_obs_evts[i] - nom_bkg_rates[i] * nom_dmc_effs[i] * veto_effs[i]) * scale_factors[i] * dmc_effs[i] / nom_dmc_effs[i] + (bkg_rates[i] * dmc_effs[i] * veto_effs[i])
    obs_evts = new_vals(obs_evt)

    def replace_line(rownum, vals, fmt="%f"):
        i = line_indices[rownum]
        part1 = " ".join(out_lines[i].split()[:2])
        part2 = " ".join(fmt % v for v in vals)
        out_lines[i] = f"{part1} {part2}\n"

    replace_line(1, obs_evts, "%d")
    replace_line(4, dmc_effs, "%.4f")
    replace_line(9, bkg_rates, "%.4f")
    replace_line(10, bkg_errs, "%.5f")
    replace_line(11, acc_rates, "%.3f")
    replace_line(12, acc_errs, "%.5f")
    replace_line(13, li9_rates, "%.4f")
    replace_line(14, li9_errs, "%.4f")
    replace_line(15, fastn_rates, "%.4f")
    replace_line(16, fastn_errs, "%.4f")
    replace_line(17, amc_rates, "%.4f")
    replace_line(18, amc_errs, "%.4f")
    replace_line(19, alphan_rates, "%.4f")
    replace_line(20, alphan_errs, "%.4f")

    for line in out_lines:
        f_out.write(line)

    f_out.close()


if __name__ == '__main__':
    main()
