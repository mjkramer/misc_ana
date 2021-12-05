#!/usr/bin/env python-3

import os

import pandas as pd

import MyROOT as R
R.gROOT.SetBatch(True)

from common import CONFIGS, TAGS
from fitter import Fitter
from fitter import DoubCrysNGdFitter, DoubCrysPlusExpNGdFitter
from fitter import DybfNGdFitter, MyDybfNGdFitter
from fitter import K40Fitter, Tl208Fitter, MeanFitter
from util import deleter


def get_tree(selname, site, det):
    treename = f'ibd_AD{det}'
    tree = R.TChain(treename)
    for nADs in [6, 8, 7]:
        path = f'input/{selname}/stage2.pbp.eh{site}.{nADs}ad.root'
        f = R.TFile(path)
        if f.Get(treename):
            tree.Add(path)
    if tree.GetEntries():
        return tree
    return None


def fit_ibd(fitter: Fitter, tree: R.TTree, branch):
    h = R.TH1F("h", "h", 120, 6, 12)
    tree.Draw(f"{branch}>>h")

    with deleter(h):
        peak, err, chi2ndf, success = fitter.fit(h)
        return peak, err, chi2ndf, success



def get_ibd_row(branch, context):
    fitter, tree, site, det = context
    peak, err, chi2ndf, success = fit_ibd(branch, fitter, tree)

    return {'site': site, 'det': det,
            'fit_peak': peak, 'fit_err': err,
            'chi2ndf': chi2ndf, 'success': success}


def get_ibd_rows(branch, selname, fitclass, site, det):
    tree = get_tree(selname, site, det)
    if not tree:
        return []
    fitter = fitclass()

    context = (fitter, tree, site, det)
    return [get_ibd_row(branch, context)]


def get_prompt_rows(*args):
    return get_ibd_rows('eP', *args)


def get_delayed_rows(*args):
    return get_ibd_rows('eD', *args)


class NoHistException(Exception):
    pass


def get_singles_hist(files, det):
    hname = f'h_single_AD{det}'
    hists = [h for f in files if (h := f.Get(hname))]
    if not hists:
        raise NoHistException
    hist = hists[0].Clone()
    for h in hists[1:]:
        hist.Add(h)
    return hist


def get_singles_row(context):
    fitter, files, site, det = context
    h = get_singles_hist(files, det)
    with deleter(h):
        peak, err, chi2ndf, success = fitter.fit(h)
        return {'site': site, 'det': det,
                'fit_peak': peak, 'fit_err': err,
                'chi2ndf': chi2ndf, 'success': success}


def get_singles_rows(selname, fitclass, site, det):
    files = [R.TFile(f'input/{selname}/stage2.pbp.eh{site}.{nADs}ad.root')
             for nADs in [6, 8, 7]]
    fitter = fitclass()

    context = (fitter, files, site, det)
    try:
        return [get_singles_row(context)]
    except NoHistException:
        return []


def dump_fits(fitclass, peakname, selname, getter):
    data = []

    for site in [1, 2, 3]:
        for det in [1, 2, 3, 4] if site == 3 else [1, 2]:
            print(f'===== EH{site}-AD{det} =====')
            rows = getter(selname, fitclass, site, det)
            data.extend(rows)

    outdir = f'data/fullfits/{selname}'
    os.system(f'mkdir -p {outdir}')
    df = pd.DataFrame(data)
    df.sort_values(['site', 'det'], inplace=True)
    df.to_csv(f'{outdir}/fullfits_{peakname}.csv', index=False)



def dump_delayed_fits(fitclass, peakname, selname):
    return dump_fits(fitclass, peakname, selname,
                     get_delayed_rows)


def dump_delayed_fits_all(tag):
    for config in CONFIGS:
        sel = f'{tag}@{config}'
        dump_delayed_fits(DoubCrysNGdFitter, 'nGd', sel)
        dump_delayed_fits(DoubCrysPlusExpNGdFitter, 'nGdExp', sel)
        dump_delayed_fits(MyDybfNGdFitter, 'nGdDyb1', sel)
        dump_delayed_fits(DybfNGdFitter, 'nGdDyb2', sel)


def dump_delayed_fits_all2():
    for tag in TAGS:
        dump_delayed_fits_all(tag)


def dump_prompt_fits(fitclass, peakname, selname):
    return dump_fits(fitclass, peakname, selname,
                     get_prompt_rows)


def dump_prompt_fits_all(tag):
    for config in CONFIGS:
        sel = f'{tag}@{config}'
        dump_prompt_fits(MeanFitter, 'PromptE', sel)


def dump_prompt_fits_all2():
    for tag in TAGS:
        dump_prompt_fits_all(tag)


def dump_singles_fits(fitclass, peakname, selname):
    return dump_fits(fitclass, peakname, selname,
                     get_singles_rows)


def dump_singles_fits_all(tag):
    for config in CONFIGS:
        sel = f'{tag}@{config}'
        dump_singles_fits(K40Fitter, 'K40', sel)
        dump_singles_fits(Tl208Fitter, 'Tl208', sel)


def dump_singles_fits_all2():
    for tag in TAGS:
        dump_singles_fits_all(tag)
