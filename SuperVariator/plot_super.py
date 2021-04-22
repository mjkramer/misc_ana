import matplotlib.pyplot as plt

from fit_result import read_full


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
