import os

import ROOT as R
from root_pandas import read_root

from util import read_ibdsel_config


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


def loadAccUncMC(selname, nADs, site, det):
    home = os.getenv("IBDSEL_HOME")
    stage2_dir = f"{home}/../data/stage2_pbp/{selname}"

    stage2_fname = f"{stage2_dir}/stage2.pbp.eh{site}.{nADs}ad.root"
    f = R.TFile(stage2_fname)
    hSing = f.Get(f"h_single_AD{det}")
    df = read_root(stage2_fname, "results").query(f"detector == {det}")

    configname = selname.split("@")[1]
    config_fname = f"{stage2_dir}/config.{configname}.txt"

    pars = params_from_config(config_fname)
    pars.livetime_s = sum(df["livetime_s"])
    pars.vetoEffSingles = sum(df["vetoEffSingles"] * df["livetime_s"]) \
        / pars.livetime_s

    return R.AccUncMC(pars, hSing)
