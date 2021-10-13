import os

import ROOT as R
from root_pandas import read_root

from util import keep, read_ibdsel_config


R.gROOT.ProcessLine(".L external/FukushimaLambertW.cc+")
R.gROOT.ProcessLine(".L AccUncMC.cc+")


def params_from_config(config_fname):
    result = R.AccUncMC.Params()
    config = read_ibdsel_config(config_fname)

    result.promptMin = config["ibdPromptEmin"]
    result.promptMax = config["ibdPromptEmax"]
    result.delayedMin = config["ibdDelayedEmin"]
    result.delayedMax = config["ibdDelayedEmax"]
    result.isolEminBefore = config["singleDmcEminBefore"]
    result.isolEmaxBefore = config["singleDmcEmaxBefore"]
    result.isolEminAfter = config["singleDmcEminAfter"]
    result.isolEmaxAfter = config["singleDmcEmaxAfter"]
    result.dmcEminBefore = config["ibdDmcEminBefore"]
    result.dmcEmaxBefore = config["ibdDmcEmaxBefore"]
    result.dmcEminAfter = config["ibdDmcEminAfter"]
    result.dmcEmaxAfter = config["ibdDmcEmaxAfter"]

    return result


def loadAccUncMC(selname, site, det, stage2_base=None, nADs_list=[6, 8, 7]):
    if stage2_base is None:
        home = os.getenv("IBDSEL_HOME")
        stage2_dir = f"{home}/../data/stage2_pbp/{selname}"
    else:
        stage2_dir = f"{stage2_base}/{selname}"

    configname = selname.split("@")[1]
    config_fname = f"{stage2_dir}/config.{configname}.txt"
    pars = params_from_config(config_fname)

    nonVetoedLivetime = 0.
    hSing = None

    for nADs in nADs_list:
        print(nADs, site, det)
        stage2_fname = f"{stage2_dir}/stage2.pbp.eh{site}.{nADs}ad.root"
        f = R.TFile(stage2_fname)
        hSingThis = f.Get(f"h_single_AD{det}")
        if not hSingThis:
            continue
        if hSing is None:
            hSing = keep(hSingThis.Clone())
        else:
            hSing.Add(hSingThis)
        df = read_root(stage2_fname, "results").query(f"detector == {det}")

        pars.livetime_s += sum(df["livetime_s"])
        nonVetoedLivetime += sum(df["vetoEffSingles"] * df["livetime_s"])

    pars.vetoEffSingles = nonVetoedLivetime / pars.livetime_s

    return R.AccUncMC(pars, hSing)
