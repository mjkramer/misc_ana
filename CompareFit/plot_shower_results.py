#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

def plot(df, vals, title, fname):
    plt.figure()
    cmap = plt.cm.get_cmap("RdYlBu")
    plt.scatter(df.muE, df.muT, c=vals, cmap=cmap)
    plt.title(f"{title} (full P17B)")
    plt.xlabel("Shower muon min P.E.")
    plt.ylabel(r"Shower muon veto ($\mu$s)")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(f"gfx/{fname}.pdf")
    plt.savefig(f"gfx/{fname}.png")

def main():
    # produce with gen_shower_results.py
    df = pd.read_csv("data/shower2.dat", sep=r"\s+")

    plot(df, df.s_best, r"Best $\sin^2 2\theta_{13}$", "s_best")
    plot(df, 0.5 * (df.s_max - df.s_min), r"$\sin^2 2\theta_{13}$ uncertainty", "s_unc")
    plot(df, df.d_best, r"Best $\Delta m^2_{ee}$", "d_best")
    plot(df, 0.5 * (df.d_max - df.d_min), r"$\Delta m^2_{ee}$ uncertainty", "d_unc")

if __name__ == '__main__':
    main()
