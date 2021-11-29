#!/usr/bin/env python3

import os

import matplotlib.pyplot as plt
import pandas as pd

from common import SELS, DIVS_R2, DIVS_Z

CORRNAMES = {'post17_v5v3v1_NL@test_newNonUni_alphas_ngd': "$\\alpha$+nGd",
             'post17_v5v3v1_NL@test_newNonUni_alphas_only': "$\\alpha$-only",
             'post17_v5v3v1_NL@test_newNonUni_off': "no corr."}

plt.rcParams.update({'font.size': 13})


def midR2(binR2):
    return 1e-6 * 0.5 * (DIVS_R2[binR2] + DIVS_R2[binR2 - 1])


def midZ(binZ):
    return 1e-3 * 0.5 * (DIVS_Z[binZ] + DIVS_Z[binZ - 1])


def get_df(sel, site, det, peak, *, relGdLS=False):
    full_df = pd.read_csv(f'data/peakmaps/{sel}/peaks_{peak}.csv')
    df = full_df.query(f'site == {site} and det == {det}').copy()
    df["midR2"] = df["binR2"].map(midR2)
    df["midZ"] = df["binZ"].map(midZ)
    if relGdLS:
        sub_df = df.query('binR2 <= 6 and binZ >= 2 and binZ <= 9')
        avg = sub_df['fit_peak'].mean()
        df['fit_peak'] /= avg
    return df


def plot_df(df, title, **kwargs):
    piv = df.pivot_table(columns="midR2", index="midZ", values="fit_peak")
    plt.pcolormesh(piv.columns, piv.index, piv.values,
                   shading="nearest", **kwargs)
    plt.colorbar()
    plt.xlabel("R$^2$ (m$^2$)")
    plt.ylabel("Z (m)")
    plt.title(title)
    plt.tight_layout()


def get_extrema(dfs):
    vmin = min(df['fit_peak'].min() for df in dfs)
    vmax = max(df['fit_peak'].max() for df in dfs)
    return vmin, vmax


def plot_grid(site, det, peak, relGdLS=False):
    dfs = [get_df(sel, site, det, peak, relGdLS=relGdLS) for sel in SELS]
    vmin, vmax = get_extrema(dfs)

    fig, axs = plt.subplots(2, 2, figsize=(14.8, 9.6))
    axs[1][1].set_axis_off()

    for sel, df, ax in zip(SELS, dfs, axs.flatten()):
        plt.sca(ax)
        suffix = ' (rel. GdLS)' if relGdLS else ''
        title = f'{peak} peak ({CORRNAMES[sel]}), EH{site}-AD{det}{suffix}'
        plot_df(df, title, vmin=vmin, vmax=vmax)

    fig.tight_layout()

    tag = SELS[0].split("@")[0]  # e.g. post17_v5v3v1_NL
    name = 'gridRel' if relGdLS else 'grid'
    gfxdir = f'gfx/{name}/{tag}'
    os.system(f'mkdir -p {gfxdir}')
    for ext in ['pdf', 'png']:
        fig.savefig(f'{gfxdir}/{name}_{peak}_eh{site}_ad{det}.{ext}')


def plot_grid_all(peak, relGdLS=False):
    sites = [1, 2, 2, 3, 3, 3, 3]
    dets = [2, 1, 2, 1, 2, 3, 4]

    for site, det in zip(sites, dets):
        plot_grid(site, det, peak, relGdLS)
