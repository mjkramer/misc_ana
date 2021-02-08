from glob import glob
import os

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import uproot

from diagnostics import get_column


mpl.rc("figure", autolayout=True, max_open_warning=0)


HALLDETS = [(1, [1, 2]),
            (2, [3, 4]),
            (3, [5, 6, 7, 8])]

HALLDETS_LOCAL = [(1, [1, 2]),
                  (2, [1, 2]),
                  (3, [1, 2, 3, 4])]


def cutnames(study):
    for cutdir in sorted(glob(f"fit_results/{study}/*")):
        cutname = os.path.basename(cutdir)
        yield cutname


def generate(func, study_or_studies, *args, **kwargs):
    study = study_or_studies[0] if type(study_or_studies) is list \
        else study_or_studies

    for cutname in cutnames(study):
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
    # fig.tight_layout()

    save(fig, f"gfx/covmat/{matname}/{study}/{matname}_{cutname}.png")


# ==============================================================================
def plot_covmat_all(study):
    for matname in ["sigsys", "bgsys"]:
        generate(plot_covmat, study, matname=matname)


def plot_chi2(study, cutname):
    path = f"fit_results/{study}/{cutname}/fit_shape_2d.root"
    f = uproot.open(path)
    z, x, y = f["h_chi2_map"].to_numpy()

    for name, norm in \
        [("linear", colors.Normalize()),
         # ("log", colors.LogNorm(vmin=z.min(), vmax=z.max()))]:
         ("log", colors.SymLogNorm(linthresh=1e-2,
                                   vmin=z.min(), vmax=z.max()))]:

        fig, ax = plt.subplots()
        pcm = ax.pcolormesh(x, y, z, norm=norm)
        fig.colorbar(pcm, ax=ax, fraction=0.1)
        ax.set(title=r"$\Delta \chi^2$",
               xlabel=r"$\sin^2 2\theta_{13}$",
               ylabel=r"$\Delta m^2_{\mathrm{ee}}$")
        # fig.tight_layout()

        save(fig, f"gfx/chi2maps/{name}/{study}/chi2_{name}_{cutname}.png")


# ==============================================================================
def plot_chi2_all(study):
    generate(plot_chi2, study)


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


def draw_hist(h, **kwargs):
    return bstep(h.axis().edges(), h.values(), **kwargs)


def _plot_input_spec(file_template, hist_template, title, dirname,
                     studies, cutname, norm=False, ratio=False):
    vals = {study: {} for study in studies}  # hall -> spectrum
    edges = None

    for study in studies:
        for nADs in [6, 8, 7]:
            fname = file_template.format(nADs=nADs)
            path = f"fit_results/{study}/{cutname}/{fname}"
            f = uproot.open(path)
            for hall, dets in HALLDETS_LOCAL:
                for det in dets:
                    hname = hist_template.format(hall=hall, det=det)
                    if hname in f:
                        h = f[hname]
                        edges = h.axis().edges()
                        if hall not in vals[study]:
                            vals[study][hall] = h.values()
                        else:
                            vals[study][hall] += h.values()

    if norm:
        for study in studies:
            for hall in [1, 2, 3]:
                vals[study][hall] /= sum(vals[study][hall])

    if ratio:
        assert len(studies) == 2
        s1, s2 = studies
        orig_vals = vals
        vals = {"_": {}}
        for hall in [1, 2, 3]:
            vals["_"][hall] = orig_vals[s1][hall] / orig_vals[s2][hall]

    fig, axs = plt.subplots(2, 2, figsize=(12.8, 9.6))
    axs = axs.flatten()
    axs[3].axis("off")

    for hall in [1, 2, 3]:
        ax = axs[hall - 1]
        for study in vals:
            bstep(edges, vals[study][hall], ax=ax, label=study)
        if len(vals) > 1:
            ax.legend()
        ax.set_xlabel("Energy [MeV]")
        ax.set_title(f"{title} spectra (EH{hall})")

    suffix = ".norm" if norm else ""
    suffix += ".ratio" if ratio else ""
    name = "+".join(studies)
    save(fig, f"gfx/{dirname}{suffix}/{name}/rawspec_{cutname}.png")


def plot_rawspec(*args, **kwargs):
    return _plot_input_spec("ibd_eprompt_shapes_{nADs}ad.root",
                            "h_ibd_eprompt_inclusive_eh{hall}_ad{det}",
                            "Raw prompt", "rawspec", *args, **kwargs)


def plot_accspec(*args, **kwargs):
    return _plot_input_spec("accidental_eprompt_shapes_{nADs}ad.root",
                            "h_accidental_eprompt_inclusive_eh{hall}_ad{det}",
                            "Accidental", "accspec", *args, **kwargs)


# ==============================================================================
def plot_rawspec_all(studies):
    for norm in [False, True]:
        for ratio in [False, True]:
            generate(plot_rawspec, studies, norm=norm, ratio=ratio)


# ==============================================================================
def plot_accspec_all(studies):
    for norm in [False, True]:
        for ratio in [False, True]:
            generate(plot_accspec, studies, norm=norm, ratio=ratio)


def get_corrspec(study, cutname, specname="IBD"):
    if specname == "TotBkg":
        return get_totbkg(study, cutname)

    edges = None
    specs = {}

    path = f"fit_results/{study}/{cutname}/fit_shape_2d.root"
    f = uproot.open(path)

    for istage in range(3):
        for hall, detnos in HALLDETS:
            for detno in detnos:
                suffix = "" if specname == "IBD" else "Spec"
                h = f[f"Corr{specname}Evts{suffix}" +
                      f"_stage{istage}_AD{detno}"]
                edges = h.axis().edges()
                if hall not in specs:
                    specs[hall] = h.values().copy()
                else:
                    specs[hall] += h.values()

    return edges, specs


def get_totbkg(study, cutname):
    specs = {}
    for bkg in ["Acc", "Li9", "Amc", "Fn", "Aln"]:
        edges, this_specs = get_corrspec(study, cutname, bkg)
        for hall in [1, 2, 3]:
            if hall not in specs:
                specs[hall] = this_specs.copy()
            else:
                specs[hall] += this_specs
    return edges, specs


def _plot_output_spec():
    pass

def plot_input(studies, key, key_err=None, **kwargs):
    fig, axs = plt.subplots(2, 2, figsize=(12.8, 9.6))
    axs = axs.flatten()
    axs[3].axis("off")

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

    fig, axs = plt.subplots(2, 2, figsize=(12.8, 9.6))
    axs = axs.flatten()
    axs[3].axis("off")

    for hall, dets in HALLDETS:
        ax = axs[hall - 1]
        xs, ys_numer = get_column(key, dets, study=studies[0], **kwargs)
        xs, ys_denom = get_column(key, dets, study=studies[1], **kwargs)
        ax.scatter(xs, ys_numer / ys_denom)
        ax.set_xlabel("Delayed min energy [MeV]")
        ax.set_title(f"{key}, {studies[0]} / {studies[1]} (EH{hall})")

    name = "+".join(studies)
    save(fig, f"gfx/input_ratio/{name}/{key}_ratio.png")


# ==============================================================================
def plot_input_all(studies, ratio=False):
    keys = ["specint",
            "obs_evt",
            "livetime",
            "mult_eff",
            "delcut_eff",
            "tot_bkg",
            "acc_bkg"]

    keys += ["li9_bkg", "fastn_bkg", "amc_bkg", "alphan_bkg", "veto_eff"]

    dontweight = ["obs_evt", "livetime"]

    fn = plot_input_ratio if ratio else plot_input

    for key in keys:
        key_err = key + "_unc" if key.endswith("_bkg") else None
        weight = key not in dontweight
        fn(studies, key, key_err, weight=weight)
