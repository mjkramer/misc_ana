from glob import glob
import os

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import uproot

from diagnostics import get_column


mpl.rcParams["figure.autolayout"] = True


HALLDETS = [(1, [1, 2]),
            (2, [3, 4]),
            (3, [5, 6, 7, 8])]


def cutnames(study):
    for cutdir in sorted(glob(f"fit_results/{study}/*")):
        cutname = os.path.basename(cutdir)
        yield cutname


def generate(func, study_or_studies, *args, **kwargs):
    study = study_or_studies[0] if type(study_or_studies) is list \
        else study_or_studies

    for cutname in cutnames(study):
        func(study_or_studies, cutname, *args, **kwargs)


def save(fig, path):
    dirname = os.path.dirname(path)
    os.system(f"mkdir -p {dirname}")
    fig.savefig(path)


def plot_covmat(study, cutname, matname="bgsys"):
    path = f"fit_results/{study}/{cutname}/covmatrices/matrix_{matname}.txt"
    mat = np.loadtxt(path)
    dim = int(np.sqrt(mat.shape[0]))
    mat.resize(dim, dim)

    fig, ax = plt.subplots(figsize=(12.8, 9.6))
    norm = colors.SymLogNorm(base=10, linthresh=1e-6, vmin=-1e-4, vmax=0.002)
    pcm = ax.pcolormesh(mat, norm=norm)
    fig.colorbar(pcm, ax=ax, fraction=0.07)
    ax.set(title=f"{matname} matrix, {cutname} delayed cut")
    # fig.tight_layout()

    save(fig, f"gfx/covmat/{matname}/{study}/{matname}_{cutname}.png")


def plot_covmat_all(study):
    for matname in ["sigsys", "bgsys"]:
        generate(plot_covmat, study, matname=matname)


def plot_chi2(study, cutname):
    path = f"fit_results/{study}/{cutname}/fit_shape_2d.root"
    f = uproot.open(path)
    z, [(x, y)] = f["h_chi2_map"].numpy()

    for name, norm in \
        [("linear", colors.Normalize()),
         ("log", colors.LogNorm(vmin=z.min(), vmax=z.max()))]:

        fig, ax = plt.subplots()
        pcm = ax.pcolormesh(x, y, z, norm=norm)
        fig.colorbar(pcm, ax=ax, fraction=0.1)
        ax.set(title=r"$\Delta \chi^2$",
               xlabel=r"$\sin^2 2\theta_{13}$",
               ylabel=r"$\Delta m^2_{\mathrm{ee}}$")
        # fig.tight_layout()

        save(fig, f"gfx/chi2maps/{name}/{study}/chi2_{name}_{cutname}.png")


def plot_chi2_all(study):
    generate(plot_chi2, study)


def plot_input(studies, key, key_err=None, **kwargs):
    fig, axs = plt.subplots(1, 3, figsize=(19.2, 4.8))

    for hall, dets in HALLDETS:
        ax = axs[hall - 1]
        for study in studies:
            def get(key):
                return get_column(key, dets, study=study, **kwargs)
            xs, ys = get(key)
            yerr = None
            if key_err:
                _, yerr = get(key_err)
            ax.errorbar(xs, ys, yerr=yerr,
                        label=study, fmt="o")
        ax.legend()
        ax.set_xlabel("Delayed min energy [MeV]")
        ax.set_title(f"{key} (EH{hall})")

    name = "+".join(studies)
    save(fig, f"gfx/input/{name}/{key}.png")


def plot_input_ratio(studies, key, key_err=None, **kwargs):
    assert len(studies) == 2

    fig, axs = plt.subplots(1, 3, figsize=(19.2, 4.8))

    for hall, dets in HALLDETS:
        ax = axs[hall - 1]
        xs, ys_numer = get_column(key, dets, study=studies[0], **kwargs)
        xs, ys_denom = get_column(key, dets, study=studies[1], **kwargs)
        ax.scatter(xs, ys_numer / ys_denom)
        ax.set_xlabel("Delayed min energy [MeV]")
        ax.set_title(f"{key}, {studies[0]} / {studies[1]} (EH{hall})")

    name = "+".join(studies)
    save(fig, f"gfx/input_ratio/{name}/{key}_ratio.png")


def plot_input_all(studies, ratio=False):
    keys = ["specint",
            "obs_evt",
            "livetime",
            "mult_eff",
            "delcut_eff",
            "tot_bkg",
            "acc_bkg"]

    dontweight = ["obs_evt", "livetime"]

    fn = plot_input_ratio if ratio else plot_input

    for key in keys:
        key_err = key + "_unc" if key.endswith("_bkg") else None
        weight = key not in dontweight
        fn(studies, key, key_err, weight=weight)
