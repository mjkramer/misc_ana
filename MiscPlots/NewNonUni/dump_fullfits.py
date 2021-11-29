#!/usr/bin/env python-3

import os

import pandas as pd

import ROOT as R
R.gROOT.SetBatch(True)

from common import SELS
from fitter import Fitter
from fitter import DoubCrysNGdFitter, DoubCrysPlusExpNGdFitter
from fitter import DybfNGdFitter, MyDybfNGdFitter
from util import deleter


def fit_ibd(fitter: Fitter, tree: R.TTree):
    h = R.TH1F("h", "h", 120, 6, 12)
    tree.Draw("eD>>h")

    with deleter(h):
        peak, err, chi2ndf, success = fitter.fit(h)
        return peak, err, chi2ndf, success


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


def get_row(context):
    fitter, tree, site, det = context
    peak, err, chi2ndf, success = fit_ibd(fitter, tree)

    return {'site': site, 'det': det,
            'fit_peak': peak, 'fit_err': err,
            'chi2ndf': chi2ndf, 'success': success}


def get_rows(selname, fitclass, site, det):
    tree = get_tree(selname, site, det)
    if not tree:
        return []
    fitter = fitclass()

    context = (fitter, tree, site, det)
    return [get_row(context)]


def dump_fits(fitclass, peakname, selname):
    data = []

    for site in [1, 2, 3]:
        for det in [1, 2, 3, 4] if site == 3 else [1, 2]:
            print(f'===== EH{site}-AD{det} =====')
            rows = get_rows(selname, fitclass, site, det)
            data.extend(rows)

    outdir = f'data/fullfits/{selname}'
    os.system(f'mkdir -p {outdir}')
    df = pd.DataFrame(data)
    df.sort_values(['site', 'det'], inplace=True)
    df.to_csv(f'{outdir}/fullfits_{peakname}.csv', index=False)


def dump_fits_all():
    for sel in SELS:
        dump_fits(DoubCrysNGdFitter, 'nGd', sel)
        dump_fits(DoubCrysPlusExpNGdFitter, 'nGdExp', sel)
        dump_fits(MyDybfNGdFitter, 'nGdDyb1', sel)
        dump_fits(DybfNGdFitter, 'nGdDyb2', sel)
