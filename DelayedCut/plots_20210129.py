from glob import glob
import os

import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import uproot


def generate(func, study_or_studies, *args, **kwargs):
    study = study_or_studies[0] if type(study_or_studies) is list \
        else study_or_studies

    for cutdir in sorted(glob(f"fit_results/{study}/*")):
        cutname = os.path.basename(cutdir)
        print(cutname)
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
    fig.tight_layout()

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
        fig.tight_layout()

        save(fig, f"gfx/chi2maps/{name}/{study}/chi2_{name}_{cutname}.png")


def plot_chi2_all(study):
    generate(plot_chi2, study)
