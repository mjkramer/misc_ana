import os

import matplotlib.pyplot as plt
import pandas as pd
import uproot

from diagnostics import theta13_to_df


def full_df(study, ident, nADs):
    direc = f"fit_results/{study}/{ident}/"
    fname = f"Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
    df = theta13_to_df(f"{direc}/{fname}")

    # Add vertex/delayed efficiencies
    df_aux = pd.read_csv(f"{direc}/aux_{fname}",
                         sep="\t", header=None, index_col=0)
    df = df.join(df_aux.transpose())

    # Add corrected # evts
    rootpath = f"fit_results/{study}/{ident}/fit_shape_2d.root"
    f = uproot.open(rootpath)
    istage = {6: 0, 8: 1, 7: 2}[nADs]
    corr_evt = []
    for detno in range(1, 9):
        hname = f"CorrIBDEvts_stage{istage}_AD{detno}"
        corr_evt.append(f[hname].values().sum())

    df["corr_evt"] = corr_evt
    return df


def savefig(fig, category, study, fname):
    direc = f"gfx/{category}/{study}"
    os.system(f"mkdir -p {direc}")
    for ext in ["png"]:
        fig.savefig(f"{direc}/{fname}.{ext}")


def plot_labeled_fits(study, qty, title, best_or_mid="best"):
    df = pd.read_csv(f"summaries/{study}.csv", index_col=0)
    if best_or_mid == "mid":
        expr = f"0.5 * ({qty}_min1sigma + {qty}_max1sigma)"
        df[f"{qty}_mid"] = df.eval(expr)

    xs = df["ident"]
    ymin = df[f"{qty}_min1sigma"]
    ymax = df[f"{qty}_max1sigma"]
    if best_or_mid == "best":
        ys = df[f"{qty}_best"]
    else:
        ys = (ymin + ymax) / 2

    yerrlow = ys - ymin
    yerrhigh = ymax - ys

    fig, ax = plt.subplots()
    ax.errorbar(xs, ys, yerr=[yerrlow, yerrhigh], fmt="o")
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    ax.set_title(title)
    fig.tight_layout()

    savefig(fig, "labeled_fit_results", study, f"{qty}_{best_or_mid}")

    return fig, ax


def plot_labeled_s2t_best(study):
    return plot_labeled_fits(study, "s2t",
                             r"$\sin^2 2\theta_{13}$ (best fit)",
                             "best")


def plot_labeled_s2t_mid(study):
    return plot_labeled_fits(study, "s2t",
                             r"$\sin^2 2\theta_{13}$ (1$\sigma$ midpoint)",
                             "mid")


def plot_labeled_dm2_best(study):
    return plot_labeled_fits(study, "dm2",
                             r"$\Delta m^2_{ee}$ (best fit)",
                             "best")


def plot_labeled_dm2_mid(study):
    return plot_labeled_fits(study, "dm2",
                             r"$\Delta m^2_{ee}$ (1$\sigma$ midpoint)",
                             "mid")


def plot_labeled_fits_all(study):
    plot_labeled_s2t_best(study)
    plot_labeled_s2t_mid(study)
    plot_labeled_dm2_best(study)
    plot_labeled_dm2_mid(study)


def plot_ratio(study="test_newDelEff", ident="zTopThird@flat", nADs=8):
    ident_nom = "fullDet@flat"

    df = full_df(study, ident, nADs)
    df_nom = full_df(study, ident_nom, nADs)

    xs = df.index

    # df["fullEff"] = df["vertexEff"] * 0.88
    # df_nom["fullEff"] = df_nom["vertexEff"] * 0.88

    df["theEff"] = df["vertexEff"] * df["mult_eff"]
    df_nom["theEff"] = df_nom["vertexEff"] * df_nom["mult_eff"]

    def ratios(col):
        return df[col] / df_nom[col]

    # ys_eff = ratios("fullEff")
    # ys_eff = ratios("vertexEff")
    ys_eff = ratios("theEff")
    ys_raw = ratios("obs_evt")
    ys_corr = ratios("corr_evt")

    fig, ax = plt.subplots()

    ax.scatter(xs, ys_eff, label="vertex eff ratio")
    ax.scatter(xs, ys_raw, label="raw events ratio")

    name = ident.split("@")[0]
    ax.legend()
    ax.set_title(f"{nADs}AD, {name}:fullDet ratio")
    fig.tight_layout()

    fig2, ax2 = plt.subplots()
    ax2.scatter(xs, ys_corr, label="corr events")
    ax2.set_title(f"{nADs}AD {name}:fullDet corr events ratio")
    fig2.tight_layout()


def plot_ratio_all_periods(study="test_newDelEff", ident="zTopThird@flat"):
    ident_nom = "fullDet@flat"

    dfs = []
    dfs_nom = []

    for nADs in [6, 8, 7]:
        df = full_df(study, ident, nADs)
        df_nom = full_df(study, ident_nom, nADs)

        xs = df.index

        # df["fullEff"] = df["vertexEff"] * 0.88
        # df_nom["fullEff"] = df_nom["vertexEff"] * 0.88

        df["theEff"] = df["vertexEff"] * df["mult_eff"]
        df_nom["theEff"] = df_nom["vertexEff"] * df_nom["mult_eff"]

        dfs.append(df)
        df_nom.append(df_nom)

    totweight = sum([df["livetime"] for df in dfs])
    print(totweight)

    def ratios(name):
        wtdsum = sum(df["livetime"] * df[name] / df_nom[name]
                     for df, df_nom in zip(dfs, dfs_nom))
        print(wtdsum)
        return wtdsum / totweight

    # ys_eff = ratios("fullEff")
    # ys_eff = ratios("vertexEff")
    ys_eff = ratios("theEff")
    ys_raw = ratios("obs_evt")
    ys_corr = ratios("corr_evt")

    fig, ax = plt.subplots()

    ax.scatter(xs, ys_eff, label="vertex eff ratio")
    ax.scatter(xs, ys_raw, label="raw events ratio")

    name = ident.split("@")[0]
    ax.legend()
    ax.set_title(f"{name}:fullDet ratio")
    fig.tight_layout()

    fig2, ax2 = plt.subplots()
    ax2.scatter(xs, ys_corr, label="corr events")
    ax2.set_title(f"{name}:fullDet corr events ratio")
    fig2.tight_layout()


def new_vertex_effs(study="test_newDelEff", ident="zTopThird@flat",
                    ident_nom="fullDet@flat"):
    # like corr_evt but without vertex (and e_d?) correction
    def add_new_corr_evt(df):
        df["new_corr_evt"] = \
            df.eval("(obs_evt - tot_bkg*veto_eff*mult_eff*livetime) / (veto_eff*mult_eff*livetime*delayedEff)")
    for stage, nADs in [(1, 6), (2, 8), (3, 7)]:
        df_cut = full_df(study, ident, nADs)
        df_nom = full_df(study, ident_nom, nADs)
        add_new_corr_evt(df_cut)
        add_new_corr_evt(df_nom)
        # XXX use actual delayed effs
        vals = df_cut["new_corr_evt"] / df_nom["new_corr_evt"] * 0.88
        vals = vals.fillna(0)
        valstr = "\t".join(["%.4f" % v for v in vals])
        print(f"{stage}\t5\t{valstr}")
