#!/usr/bin/env python3

import os

import matplotlib.pyplot as plt
import pandas as pd

from common import CONFIGS, TAGS

plt.rcParams.update({'font.size': 13})


def get_df(tag: str, config: str, peak: str):
    df = pd.read_csv(f'data/fullfits/{tag}@{config}/fullfits_{peak}.csv')
    assert isinstance(df, pd.DataFrame)
    df["AD"] = 2 * (df["site"] - 1) + df["det"]
    df["label"] = [f'EH{site}-AD{det}'
                   for (site, det) in zip(df['site'], df['det'])]
    return df


def plot_df(df, title, ylim=None, **kwargs):
    plt.errorbar(df["AD"], df['fit_peak'], yerr=df['fit_err'],
                 fmt='o', **kwargs)
    xmin = 2 if len(df) == 7 else 1
    plt.xlim(xmin - 0.5, 8.5)
    if ylim:
        plt.ylim(*ylim)
    plt.xticks(range(xmin, 9), df["label"])
    plt.ylabel("Peak location (MeV)")
    plt.title(title)
    plt.tight_layout()


def get_extrema(dfs):
    ymin = min((df['fit_peak'] - df['fit_err']).min() for df in dfs)
    ymax = max((df['fit_peak'] + df['fit_err']).max() for df in dfs)
    rng = ymax - ymin
    return ymin - rng / 20, ymax + rng / 20


def plot_fullGrid(tag: str, peak: str):
    dfs = [get_df(tag, config, peak)
           for config in CONFIGS]
    ylim = get_extrema(dfs)

    fig: plt.Figure = plt.figure(figsize=(12.2, 9.6))
    gs = fig.add_gridspec(4, 4)
    axs = [fig.add_subplot(gs[r:r+2, c:c+2])
           for (r, c) in [(0, 0), (0, 2), (2, 1)]]

    for config, df, ax in zip(CONFIGS, dfs, axs):
        plt.sca(ax)
        title = f'{peak} peak ({CONFIGS[config]}), {TAGS[tag]}'
        plot_df(df, title, ylim=ylim)

    fig.tight_layout()

    gfxdir = f'gfx/fullfits/{TAGS[tag]}'
    os.system(f'mkdir -p {gfxdir}')
    for ext in ['png']:
        fig.savefig(f'{gfxdir}/fullfits_{peak}.{ext}')


def plot_fullGrid_all2(tag, /, **kwargs):
    for peak in ['nGdExp', 'K40', 'Tl208', 'PromptE']:
        plot_fullGrid(tag, peak, **kwargs)


def plot_fullGrid_all3(**kwargs):
    for tag in TAGS:
        plot_fullGrid_all2(tag, **kwargs)
