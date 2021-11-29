#!/usr/bin/env python3

import os

import matplotlib.pyplot as plt
import pandas as pd

from common import SELS

CORRNAMES = {'post17_v5v3v1_NL@test_newNonUni_alphas_ngd': "$\\alpha$+nGd",
             'post17_v5v3v1_NL@test_newNonUni_alphas_only': "$\\alpha$-only",
             'post17_v5v3v1_NL@test_newNonUni_off': "no corr."}

plt.rcParams.update({'font.size': 13})


def get_df(sel, peak):
    df = pd.read_csv(f'data/fullfits/{sel}/fullfits_{peak}.csv')
    df["AD"] = 2 * (df["site"] - 1) + df["det"]
    df["label"] = [f'EH{site}-AD{det}'
                   for (site, det) in zip(df['site'], df['det'])]
    return df


def plot_df(df, title, ylim=None, **kwargs):
    plt.errorbar(df["AD"], df['fit_peak'], yerr=df['fit_err'],
                 fmt='o', **kwargs)
    plt.xlim(1.5, 8.5)
    if ylim:
        plt.ylim(*ylim)
    plt.xticks(range(2, 9), df["label"])
    plt.ylabel("Peak location (MeV)")
    plt.title(title)
    plt.tight_layout()


def get_extrema(dfs):
    ymin = min((df['fit_peak'] - df['fit_err']).min() for df in dfs)
    ymax = max((df['fit_peak'] + df['fit_err']).max() for df in dfs)
    rng = ymax - ymin
    return ymin - rng / 20, ymax + rng / 20


def plot_fullGrid(peak):
    dfs = [get_df(sel, peak) for sel in SELS]
    ylim = get_extrema(dfs)

    fig, axs = plt.subplots(2, 2, figsize=(14.8, 9.6))
    axs[1][1].set_axis_off()

    for sel, df, ax in zip(SELS, dfs, axs.flatten()):
        plt.sca(ax)
        title = f'{peak} peak ({CORRNAMES[sel]})'
        plot_df(df, title, ylim=ylim)

    fig.tight_layout()

    tag = SELS[0].split("@")[0]  # e.g. post17_v5v3v1_NL
    gfxdir = f'gfx/fullfits/{tag}'
    os.system(f'mkdir -p {gfxdir}')
    for ext in ['pdf', 'png']:
        fig.savefig(f'{gfxdir}/fullfits_{peak}.{ext}')


def plot_fullGrid_all():
    for peak in ['nGd', 'nGdExp', 'nGdDyb1', 'nGdDyb2']:
        plot_fullGrid(peak)
