import os

import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial import polynomial
# from scipy.optimize import curve_fit
from root_pandas import read_root

from diagnostics import dataframes, get_column


def get_col_between(colname, dets, mincut, maxcut, *args, **kwargs):
    xs_, ys_ = get_column(colname, dets, *args, **kwargs)
    pts = [(x, y) for x, y in zip(xs_, ys_)
           if mincut <= x <= maxcut]
    xs, ys = zip(*pts)
    return np.array(xs), np.array(ys)


def plot_acc_resid(study, mincut=4, maxcut=5):
    fig, axs = plt.subplots(figsize=[12.8, 9.6],
                            nrows=2, ncols=2)

    near = [1, 2, 3, 4]
    far = [5, 6, 7, 8]

    for i, dets in enumerate([near, far]):
        xs, ys = get_col_between("acc_bkg", dets, mincut, maxcut)
        # XXX get rid of np.flip if we upgrade numpy
        coefs = np.flip(polynomial.polyfit(xs, ys, 6))
        poly = np.poly1d(coefs)
        ys_poly = poly(xs)
        ys_resid = (ys - ys_poly) / ys_poly

        xs_fine = np.linspace(mincut, maxcut, 100)
        ys_poly_fine = poly(xs_fine)

        hallsname = "near halls" if dets == near else "far hall"

        ax = axs[0][i]
        ax.scatter(xs, ys)
        ax.plot(xs_fine, ys_poly_fine, c='g')
        ax.set(title=f"Accidentals rate ({hallsname})",
               xlabel="Delayed cut [MeV]")

        ax = axs[1][i]
        ax.scatter(xs, ys_resid)
        ax.axhline(0, c='g')
        ax.set(title=f"Rel. residuals after fit ({hallsname})",
               xlabel="Delayed cut [MeV]")

    fig.tight_layout()

    os.system("mkdir -p gfx/acc_resid")
    fig.savefig(f"gfx/acc_resid/acc_resid.{study}.png")



def find_stage2_dir(cut):
    isfirst = np.isclose(cut % 0.1, 0.1)
    isfirst = isfirst or np.isclose(cut % 0.1, 0)
    name = "first" if isfirst else "fine4to5"
    digits = 2 if isfirst else 3
    cutname = f"%.{digits}fMeV" % cut
    p = f"~/mywork/ThesisAnalysis/IbdSel/data/stage2_pbp/2020_01_26@delcut_{name}_{cutname}"
    p = os.path.expanduser(p)
    print(p)
    assert os.path.exists(p)
    return p


def plot_results_col(col, hall, mincut=4, maxcut=5):
    fig, axs = plt.subplots(figsize=[6.4, 9.6], nrows=2)

    xs = [x for x in sorted(dataframes().keys())
          if mincut <= x <= maxcut]
    ys = []

    for cut in xs:
        direc = find_stage2_dir(cut)
        paths = [f"{direc}/stage2.pbp.eh{hall}.{N}ad.root"
                 for N in [6, 8, 7]]
        df = read_root(paths, "results")
        val = sum(df[col] * df["livetime_s"]) / sum(df["livetime_s"])
        ys.append(val)

    # XXX
    coefs = np.flip(polynomial.polyfit(xs, ys, 6))
    poly = np.poly1d(coefs)
    ys_poly = poly(xs)
    ys_resid = (ys - ys_poly) / ys_poly

    xs_fine = np.linspace(mincut, maxcut, 100)
    ys_poly_fine = poly(xs_fine)

    ax = axs[0]
    ax.scatter(xs, ys)
    ax.plot(xs_fine, ys_poly_fine, c="g")
    ax.set(title=f"{col} (EH{hall})",
           xlabel="Delayed cut [MeV]")

    ax = axs[1]
    ax.scatter(xs, ys_resid)
    ax.axhline(0, c="g")
    ax.set(title=f"{col} residuals after fit (EH{hall})",
           xlabel="Delayed cut [MeV]")

    fig.tight_layout()

    os.system("mkdir -p gfx/results_resid")
    fig.savefig(f"gfx/results_resid/{col}_eh{hall}.png")


def plot_dlike(*args, **kwargs):
    for hall in [1, 2, 3]:
        plot_results_col("delayedLikeHz", hall, *args, **kwargs)


def plot_plike(*args, **kwargs):
    for hall in [1, 2, 3]:
        plot_results_col("promptLikeHz", hall, *args, **kwargs)
