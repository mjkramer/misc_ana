#!/usr/bin/env python3

from itertools import chain, product
from multiprocessing import Pool
import os

import numpy as np
import pandas as pd

import ROOT as R
R.gROOT.SetBatch(True)

from common import DIVS_R2, DIVS_Z, SELS
from fitter import Fitter
from fitter import DoubCrysNGdFitter, DoubCrysPlusExpNGdFitter
from fitter import DybfNGdFitter, MyDybfNGdFitter
from util import deleter

NUM_PROCS = 20


def get_vtx_cut(r2bounds, zbounds, suffix):
    "suffix is P or D (prompt or delayed)"
    r2min, r2max = r2bounds
    zmin, zmax = zbounds

    x, y, z = f'x{suffix}', f'y{suffix}', f'z{suffix}'
    r2 = f'({x}*{x} + {y}*{y})'
    conds = []
    if r2min is not None:
        conds.append(f'{r2} >= {r2min}')
    if r2max is not None:
        conds.append(f'{r2} < {r2max}')
    if zmin is not None:
        conds.append(f'{z} >= {zmin}')
    if zmax is not None:
        conds.append(f'{z} < {zmax}')

    return ' && '.join(conds)


def fit_ibd(fitter: Fitter, tree: R.TTree, r2bounds, zbounds):
    cut = get_vtx_cut(r2bounds, zbounds, 'D')
    print(cut)

    h = R.TH1F("h", "h", 120, 6, 12)
    tree.Draw("eD>>h", cut)

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


def get_row(context, binR2, binZ):
    fitter, tree, site, det = context

    r2min, r2max = DIVS_R2[binR2 - 1], DIVS_R2[binR2]
    zmin, zmax = DIVS_Z[binZ - 1], DIVS_Z[binZ]

    peak, err, chi2ndf, success = \
        fit_ibd(fitter, tree, (r2min, r2max), (zmin, zmax))

    return {'site': site, 'det': det, 'binR2': binR2, 'binZ': binZ,
            'fit_peak': peak, 'fit_err': err,
            'chi2ndf': chi2ndf, 'success': success}


def get_rows(selname, fitclass, site, det, bins):
    tree = get_tree(selname, site, det)
    if not tree:
        return []
    fitter = fitclass()
    context = (fitter, tree, site, det)

    return [get_row(context, binR2, binZ)
            for (binR2, binZ) in bins]

    # args = product([context],
    #                range(1, len(DIVS_R2)),
    #                range(1, len(DIVS_Z)))

    # # data = []
    # # for context, binR2, binZ in args:
    # #     data.append(get_row(context, binR2, binZ))

    # data = Pool(processes=20).starmap(get_row, args)

    # return data


def dump_fits(fitclass, peakname, selname):
    data = []

    for site in [1, 2, 3]:
        for det in [1, 2, 3, 4] if site == 3 else [1, 2]:
            print(f'===== EH{site}-AD{det} =====')
            allbins = list(product(range(1, len(DIVS_R2)),
                                   range(1, len(DIVS_Z))))
            bin_chunks = list(np.array_split(allbins, NUM_PROCS))
            args = product([selname], [fitclass], [site], [det],
                           bin_chunks)
            # rows = get_rows(fitter, tree, site, det)
            rows = Pool(processes=NUM_PROCS).starmap(get_rows, args)
            data.extend(chain(*rows))

    outdir = f'data/peakmaps/{selname}'
    os.system(f'mkdir -p {outdir}')
    df = pd.DataFrame(data)
    df.sort_values(['site', 'det', 'binR2', 'binZ'], inplace=True)
    df.to_csv(f'{outdir}/peaks_{peakname}.csv', index=False)


def dump_fits_all():
    for sel in SELS:
        dump_fits(DoubCrysNGdFitter, 'nGd', sel)
        dump_fits(DoubCrysPlusExpNGdFitter, 'nGdExp', sel)
        dump_fits(MyDybfNGdFitter, 'nGdDyb1', sel)
        dump_fits(DybfNGdFitter, 'nGdDyb2', sel)
