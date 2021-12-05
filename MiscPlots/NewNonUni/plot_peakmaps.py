#!/usr/bin/env python3

import os

import matplotlib as mpl
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
    assert isinstance(full_df, pd.DataFrame)
    df = full_df.query(f'site == {site} and det == {det}').copy() # type:ignore
    assert isinstance(df, pd.DataFrame)
    df["midR2"] = df["binR2"].map(midR2)
    df["midZ"] = df["binZ"].map(midZ)
    if relGdLS:
        sub_df = df.query('binR2 <= 6 and binZ >= 2 and binZ <= 9')
        assert isinstance(sub_df, pd.DataFrame)
        avg = sub_df['fit_peak'].mean()
        df['fit_peak'] /= avg
    return df


def plot_df(df, title, *, colorbar=False, **kwargs):
    piv = df.pivot_table(columns="midR2", index="midZ", values="fit_peak")
    plt.pcolormesh(piv.columns, piv.index, piv.values,
                   shading="nearest", **kwargs)
    if colorbar:
        plt.colorbar()
    plt.xlabel("R$^2$ (m$^2$)")
    plt.ylabel("Z (m)")
    plt.title(title)
    plt.tight_layout()


def get_extrema(dfs):
    vmin = min(df['fit_peak'].min() for df in dfs)
    vmax = max(df['fit_peak'].max() for df in dfs)
    return vmin, vmax


def plot_grid(site, det, peak, *, relGdLS=False, autorange=False, **kwargs):
    dfs = [get_df(sel, site, det, peak, relGdLS=relGdLS) for sel in SELS]
    if autorange:
        vmin, vmax = get_extrema(dfs)
        kwargs |= dict(vmin=vmin, vmax=vmax)

    fig: plt.Figure = plt.figure(figsize=(12.2, 9.6))
    gs = fig.add_gridspec(4, 4)
    axs = [fig.add_subplot(gs[r:r+2, c:c+2])
           for (r, c) in [(0, 0), (0, 2), (2, 1)]]

    for sel, df, ax in zip(SELS, dfs, axs):
        plt.sca(ax)
        suffix = ' (rel. GdLS)' if relGdLS else ''
        title = f'{peak} peak ({CORRNAMES[sel]}), EH{site}-AD{det}{suffix}'
        plot_df(df, title, **kwargs)

    fig.tight_layout()

    tag = SELS[0].split("@")[0]  # e.g. post17_v5v3v1_NL
    name = 'gridRel' if relGdLS else 'grid'
    gfxdir = f'gfx/{name}/{tag}'
    os.system(f'mkdir -p {gfxdir}')
    for ext in ['pdf', 'png', 'svg', 'eps']:
        fig.savefig(f'{gfxdir}/{name}_{peak}_eh{site}_ad{det}.{ext}')


def plot_grid_all(peak, relGdLS=False):
    sites = [1, 2, 2, 3, 3, 3, 3]
    dets = [2, 1, 2, 1, 2, 3, 4]

    for site, det in zip(sites, dets):
        plot_grid(site, det, peak, relGdLS=relGdLS)


def plot_grid_all_all(relGdLS=False):
    for peak in ['nGd', 'nGdExp', 'nGdDyb1', 'nGdDyb2']:
        plot_grid_all(peak, relGdLS)


def plot_grid_all_all_singles(relGdLS=False):
    for peak in ['K40', 'Tl208']:
        plot_grid_all(peak, relGdLS)


def just_colorbar(vmin: float, vmax: float):
    fig, ax = plt.subplots(figsize=(1.25, 9.6))
    fig.subplots_adjust(top=1, bottom=0, right=0.65)
    cmap = plt.rcParams['image.cmap']
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax) # type:ignore
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax) # type:ignore
