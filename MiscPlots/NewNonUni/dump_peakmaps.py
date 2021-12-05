#!/usr/bin/env python3

from itertools import chain, product
from multiprocessing import Pool
import os

import numpy as np
import pandas as pd

import MyROOT as R
R.gROOT.SetBatch(True)

from common import CONFIGS, DIVS_R2, DIVS_Z, TAGS
from fitter import Fitter, MeanFitter
from fitter import DoubCrysNGdFitter, DoubCrysPlusExpNGdFitter
from fitter import DybfNGdFitter, MyDybfNGdFitter
from fitter import K40Fitter, Tl208Fitter
from util import deleter

NUM_PROCS = 20


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


def fit_ibd(fitter: Fitter, tree: R.TTree, branch, r2bounds, zbounds):
    cut = get_vtx_cut(r2bounds, zbounds, 'D')
    print(cut)

    h = R.TH1F("h", "h", 240, 0, 12)
    tree.Draw(f"{branch}>>h", cut)

    with deleter(h):
        peak, err, chi2ndf, success = fitter.fit(h)
        return peak, err, chi2ndf, success


def get_ibd_row(branch, context, binR2, binZ):
    fitter, tree, site, det = context

    r2min, r2max = DIVS_R2[binR2 - 1], DIVS_R2[binR2]
    zmin, zmax = DIVS_Z[binZ - 1], DIVS_Z[binZ]

    peak, err, chi2ndf, success = \
        fit_ibd(fitter, tree, branch,
                (r2min, r2max), (zmin, zmax))

    return {'site': site, 'det': det, 'binR2': binR2, 'binZ': binZ,
            'fit_peak': peak, 'fit_err': err,
            'chi2ndf': chi2ndf, 'success': success}


def get_ibd_rows(branch, selname, fitclass, site, det, bins):
    tree = get_tree(selname, site, det)
    if not tree:
        return []
    fitter = fitclass()
    context = (fitter, tree, site, det)

    return [get_ibd_row(branch, context, binR2, binZ)
            for (binR2, binZ) in bins]


def get_prompt_rows(*args):
    return get_ibd_rows('eP', *args)


def get_delayed_rows(*args):
    return get_ibd_rows('eD', *args)


class NoHistException(Exception):
    pass


def get_singles_hist(files, det, binR2, binZ):
    hname = f'h_single_AD{det}_r2_{binR2}_z_{binZ}'
    hists = [h for f in files if (h := f.Get(hname))]
    if not hists:
        raise NoHistException
    hist = hists[0].Clone()
    for h in hists[1:]:
        hist.Add(h)
    return hist


def get_singles_row(context, binR2, binZ):
    fitter, files, site, det = context
    h = get_singles_hist(files, det, binR2, binZ)
    with deleter(h):
        peak, err, chi2ndf, success = fitter.fit(h)
        return {'site': site, 'det': det, 'binR2': binR2, 'binZ': binZ,
                'fit_peak': peak, 'fit_err': err,
                'chi2ndf': chi2ndf, 'success': success}


def get_singles_rows(selname, fitclass, site, det, bins):
    files = [R.TFile(f'input/{selname}/stage2.pbp.eh{site}.{nADs}ad.root')
             for nADs in [6, 8, 7]]
    fitter = fitclass()

    context = (fitter, files, site, det)
    try:
        return [get_singles_row(context, binR2, binZ)
                for (binR2, binZ) in bins]
    except NoHistException:
        return []


def dump_fits(fitclass, peakname, selname, getter):
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
            rows = Pool(processes=NUM_PROCS).starmap(getter, args)
            data.extend(chain(*rows))

    outdir = f'data/peakmaps/{selname}'
    os.system(f'mkdir -p {outdir}')
    df = pd.DataFrame(data)
    df.sort_values(['site', 'det', 'binR2', 'binZ'], inplace=True)
    df.to_csv(f'{outdir}/peaks_{peakname}.csv', index=False)


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
