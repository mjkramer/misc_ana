import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

from fit_result import read_full, read_cuts, read_study


def bstep(edges, vals, ax=None, drop2zero=True, **kwargs):
    """A better step plotter, giving ROOT-like output.
    Args:
        edges: Bin edges, length N+1.
        vals: Bin values, length N.
        ax (Optional): Axis, defaults to gca().
        drop2zero (Optional): Whether to drop down to zero on the left and
            right edges, as ROOT does. Defaults to True.
    """
    if drop2zero:
        edges = np.hstack([edges[0], edges])
        vals = np.hstack([0, vals, 0])
    else:
        vals = np.hstack([vals, vals[-1]])

    if ax is None:
        ax = plt.gca()

    return ax.step(edges, vals, where="post", **kwargs)


def bhist(a, bins=10, range=None, **kwargs):
    """A better histogram plotter, based on bstep.
    kwargs are passed to bstep.
    """
    vals, edges = np.histogram(a, bins=bins, range=range)
    return bstep(edges, vals, **kwargs)


def plot_scatter(study, qty="s2t", method="best"):
    df = read_full(study)

    fig, axs = plt.subplots(nrows=5, sharex=True, figsize=(10, 9))

    xs = df["title"]

    yerr = 0.5 * (df[f"{qty}_max1sigma"] - df[f"{qty}_min1sigma"])
    axs[0].errorbar(xs, df[f"{qty}_{method}"], yerr=yerr)
    # axs[0].set_ylabel(qty)
    axs[0].set_title(qty)

    cuts = ["shower_pe", "shower_sec",
            "delayed_emin_mev", "prompt_emin_mev"]

    for i, cut in enumerate(cuts, start=1):
        axs[i].scatter(xs, df[cut])
        # axs[i].set_ylabel(cut)
        axs[i].set_title(cut)

    # axs[0].set_title(qty)
    fig.tight_layout()

    return fig, axs


def plot_scatter_both(study, method="best"):
    gfxdir = f"gfx/scatter/{study}"
    os.system(f"mkdir -p {gfxdir}")

    df = read_full(study)

    fig, axs = plt.subplots(nrows=6, sharex=True, figsize=(10, 15))

    xs = df["title"]

    for i, qty in enumerate(["s2t", "dm2"]):
        yerr = 0.5 * (df[f"{qty}_max1sigma"] - df[f"{qty}_min1sigma"])
        axs[i].errorbar(xs, df[f"{qty}_{method}"], yerr=yerr)
        # axs[0].set_ylabel(qty)
        units = "" if qty == "s2t" else " (eV$^2$)"
        axs[i].set(ylabel=(QTY_XLABELS[qty] + units),
                   title=QTY_XLABELS[qty],
                   xticklabels=[])

    cuts = ["shower_pe", "shower_sec",
            "delayed_emin_mev", "prompt_emin_mev"]

    for i, cut in enumerate(cuts, start=2):
        axs[i].scatter(xs, df[cut])
        axs[i].set(title=CUT_TITLES[cut],
                   ylabel=CUT_XLABELS[cut],
                   xticklabels=[])
        # axs[i].set_ylabel(cut)
        # axs[i].set_title(cut)

    # axs[0].set_title(qty)
    fig.tight_layout()
    fig.savefig(f"{gfxdir}/scatter_both_{method}.pdf")

    return fig, axs


def plot_scatter_both_all(study):
    plot_scatter_both(study, "best")
    plot_scatter_both(study, "mid")


QTY_RANGES = {
    "s2t": (0.083, 0.087),
    "dm2": (0.00244, 0.00254)
}

QTY_YLABELS = {
    "s2t": r"# cuts / $4\times10^{-4}$",
    "dm2": r"# cuts / $10^{-5}$ eV$^2$"
}

QTY_XLABELS = {
    "s2t": r"$\sin^2 2\theta_{13}$",
    "dm2": r"$\Delta m^2_{ee}$"
}

def plot_qty_hists(study, bins=10, overlay_curve=False, **kwargs):
    gfxdir = f"gfx/qty_hists/{study}"
    os.system(f"mkdir -p {gfxdir}")

    df = read_study(study)

    means = {"s2t": 0.0845, "dm2": 0.00250}
    sigmas = {"s2t": 0.0037, "dm2": 0.000091}

    for qty in ["s2t", "dm2"]:
        for method in ["best", "mid"]:
            name = f"{qty}_{method}"
            fig, ax = plt.subplots()
            bhist(df[name], bins=bins, range=QTY_RANGES[qty], ax=ax, **kwargs)
            ax.set(title=QTY_XLABELS[qty] + " distribution",
                   xlabel=QTY_XLABELS[qty],
                   ylabel=QTY_YLABELS[qty])
            # ax.set_title(name)

            if overlay_curve:
                dist = norm(loc=means[qty], scale=sigmas[qty])
                x = np.linspace(df[name].min(), df[name].max(), 100)
                ax.plot(x, dist.pdf(x))

            fig.tight_layout()
            fig.savefig(f"{gfxdir}/{name}.pdf")

CUT_TITLES = {
    "shower_pe": "Shower-muon charge threshold",
    "shower_sec": "Shower-muon veto time",
    "delayed_emin_mev": "Minimum delayed energy",
    "prompt_emin_mev": "Minimum prompt energy"
}

CUT_XLABELS = {
    "shower_pe": "Threshold (photoelectrons)",
    "shower_sec": "Veto time (seconds)",
    "delayed_emin_mev": "Minimum delayed energy (MeV)",
    "prompt_emin_mev": "Minimum prompt energy (MeV)"
}

CUT_RANGES = {
    "shower_pe": (2.2e5, 4.6e5),
    "shower_sec": (0.25, 2),
    "delayed_emin_mev": (5, 7),
    "prompt_emin_mev": (0.5, 1)
}

CUT_YLABELS = {
    "shower_pe": "# cuts / 0.24 photoelectrons",
    "shower_sec": "# cuts / 0.175 seconds",
    "delayed_emin_mev": "# cuts / 0.2 MeV",
    "prompt_emin_mev": "# cuts / 0.05 MeV"
}

def plot_cut_hists(study, cut="all", **kwargs):
    gfxdir = f"gfx/cut_hists/{study}"
    os.system(f"mkdir -p {gfxdir}")

    if cut == "all":
        cuts = ["shower_pe", "shower_sec",
                "delayed_emin_mev", "prompt_emin_mev"]
    else:
        cuts = [cut]

    df = read_cuts(study)

    for cut in cuts:
        fig, ax = plt.subplots()
        bhist(df[cut], ax=ax, range=CUT_RANGES[cut], **kwargs)
        ax.set(title=CUT_TITLES[cut],
               xlabel=CUT_XLABELS[cut],
               ylabel=CUT_YLABELS[cut])
        # ax.set_title(f"{study}: {cut}")

        fig.tight_layout()
        fig.savefig(f"{gfxdir}/{cut}.pdf")
