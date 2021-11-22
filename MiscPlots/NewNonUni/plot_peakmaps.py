#!/usr/bin/env python3

import os

import matplotlib.pyplot as plt
import pandas as pd

from dump_peaks import SELS, DIVS_R2, DIVS_Z

CORRNAMES = {SELS[0]: "no",
             SELS[1]: "alphas+nGd",
             SELS[2]: "alphas-only"}


def midR2(binR2):
    return 1e-6 * 0.5 * (DIVS_R2[binR2] + DIVS_R2[binR2 - 1])


def midZ(binZ):
    return 1e-3 * 0.5 * (DIVS_Z[binZ] + DIVS_Z[binZ - 1])


def get_df(sel, site, det):
    full_df = pd.read_csv(f'data/peakmaps/{sel}/peaks_nGd.csv')
    df = full_df.query(f'site == {site} and det == {det}').copy()
    df["midR2"] = df["binR2"].map(midR2)
    df["midZ"] = df["binZ"].map(midZ)
    return df


def plot_nGd(df, title, **kwargs):
    piv = df.pivot_table(columns="midR2", index="midZ", values="peak_nGd")
    plt.pcolormesh(piv.columns, piv.index, piv.values,
                   shading="nearest", **kwargs)
    plt.colorbar()
    plt.xlabel("R$^2$ (m$^2$)")
    plt.ylabel("Z (m)")
    plt.title(title)
    plt.tight_layout()


def get_extrema(dfs):
    vmin = min(df['peak_nGd'].min() for df in dfs)
    vmax = max(df['peak_nGd'].max() for df in dfs)
    return vmin, vmax


def plot_nGd_grid(site, det):
    dfs = [get_df(sel, site, det) for sel in SELS]
    vmin, vmax = get_extrema(dfs)

    fig, axs = plt.subplots(2, 2, figsize=(12.8, 9.6))
    axs[1][1].set_axis_off()

    for sel, df, ax in zip(SELS, dfs, axs.flatten()):
        plt.sca(ax)
        title = f'nGd peak ({CORRNAMES[sel]} corr.), EH{site}-AD{det}, post-P17B'
        plot_nGd(df, title, vmin=vmin, vmax=vmax)

    fig.tight_layout()

    tag = SELS[0].split("@")[0] # e.g. post17_v5v3v1
    gfxdir = f'gfx/nGd_grid/{tag}'
    os.system(f'mkdir -p {gfxdir}')
    for ext in ['pdf', 'png']:
        fig.savefig(f'{gfxdir}/nGd_grid_eh{site}_ad{det}.{ext}')


def plot_nGd_grid_all():
    sites = [1, 2, 2, 3, 3, 3, 3]
    dets = [2, 1, 2, 1, 2, 3, 4]

    for site, det in zip(sites, dets):
        plot_nGd_grid(site, det)
