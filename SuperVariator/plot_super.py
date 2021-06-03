import matplotlib.pyplot as plt
import numpy as np

from fit_result import read_full, read_cuts


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


def plot_super(study, qty="s2t"):
    df = read_full(study)

    fig, axs = plt.subplots(nrows=5, sharex=True, figsize=(10, 9))

    xs = df["title"]

    yerr = 0.5 * (df[f"{qty}_max1sigma"] - df[f"{qty}_min1sigma"])
    axs[0].errorbar(xs, df[f"{qty}_best"], yerr=yerr)
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


def plot_cuts(study, cut="all", **kwargs):
    if cut == "all":
        cuts = ["shower_pe", "shower_sec",
                "delayed_emin_mev", "prompt_emin_mev"]
    else:
        cuts = [cut]

    df = read_cuts(study)

    for cut in cuts:
        fig, ax = plt.subplots()
        bhist(df[cut], ax=ax, **kwargs)
        ax.set_title(f"{study}: {cut}")
        fig.tight_layout()
