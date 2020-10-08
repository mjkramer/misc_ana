#!/usr/bin/env python3

from functools import lru_cache
from root_pandas import read_root
import pandas as pd
import matplotlib.pyplot as plt


@lru_cache()
def get_df():
    parts = [read_root(f"stage2_pbp/stage2.pbp.eh{hall}.{N}ad.root", "results")
             for hall in [1, 2, 3] for N in [6, 8, 7]]
    return pd.concat(parts).reset_index(drop=True)


def mean_veto_eff(tbl):
    return sum(tbl.vetoEff * tbl.livetime_s) / sum(tbl.livetime_s)


def plot_scattered(hall, det, *args, **kwargs):
    "Use a totally new random sample at each point"
    tbl = get_df().query(f"site == {hall} and detector == {det}")
    sizes = range(1, len(tbl)+1)
    vals = [mean_veto_eff(tbl.sample(N)) for N in sizes]
    plt.plot(sizes, vals, *args, **kwargs)
    plt.plot(sizes, len(sizes) * [1.001*vals[-1]], '--k')
    plt.plot(sizes, len(sizes) * [0.999*vals[-1]], '--k')


def plot_smooth(hall, det, *args, **kwargs):
    "Incrementally build up a single sample"
    tbl = get_df().query(f"site == {hall} and detector == {det}")
    sizes = range(1, len(tbl)+1)
    vals = []
    randtbl = pd.DataFrame().reindex(columns=tbl.columns)

    for _ in sizes:
        row = tbl.sample()
        tbl = tbl.drop(row.index)
        randtbl = pd.concat([randtbl, row])
        vals.append(mean_veto_eff(randtbl))

    plt.plot(sizes, vals, *args, **kwargs)
    plt.plot(sizes, len(sizes) * [1.001*vals[-1]], '--k')
    plt.plot(sizes, len(sizes) * [0.999*vals[-1]], '--k')
