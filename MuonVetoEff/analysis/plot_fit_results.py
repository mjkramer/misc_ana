from dataclasses import dataclass, asdict
from functools import lru_cache
from glob import glob
import math
import os

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import ROOT as R
import pandas as pd

try:
    from mplhacks import mplhacks
    mplhacks()
except Exception:
    pass

# HACK
class MyScalarFormatter(matplotlib.ticker.ScalarFormatter):
    def __init__(self, offset_decimals=3, *a, **kw):
        self.offset_decimals = offset_decimals
        matplotlib.ticker.ScalarFormatter.__init__(self, *a, **kw)

    def format_offset(self, value):
        # docstring inherited
        e = math.floor(math.log10(abs(value)))
        s = round(value / 10**e, 10)
        exponent = self._format_maybe_minus_and_locale("%d", e)
        significand = self._format_maybe_minus_and_locale(
            # "%d" if s % 1 == 0 else "%1.10f", s)
            "%d" if s % 1 == 0 else f"%1.{self.offset_decimals}f", s)
        if e == 0:
            return significand
        elif self._useMathText or self._usetex:
            exponent = "10^{%s}" % exponent
            return (exponent if s == 1  # reformat 1x10^y as 10^y
                    else rf"{significand} \times {exponent}")
        else:
            return f"{significand}e{exponent}"

    def get_offset(self):
        """
        Return scientific notation, plus offset.
        """
        if len(self.locs) == 0:
            return ''
        s = ''
        if self.orderOfMagnitude or self.offset:
            offsetStr = ''
            sciNotStr = ''
            if self.offset:
                # offsetStr = self.format_data(self.offset)

                # my old version here
                # another hack, sigh. want e+3, not e+03.
                # if self.offset_format.endswith("e"):
                #     ndecimals = int(self.offset_format[-2])
                # offsetStr = self.offset_format % self.offset

                print(self.offset)
                offsetStr = self.format_offset(self.offset)
                # if self.offset > 0:
                #     offsetStr = '+' + offsetStr
            if self.orderOfMagnitude:
                if self._usetex or self._useMathText:
                    sciNotStr = self.format_data(10 ** self.orderOfMagnitude)
                else:
                    sciNotStr = '1e%d' % self.orderOfMagnitude
            if self._useMathText or self._usetex:
                if sciNotStr != '':
                    sciNotStr = r'\times\mathdefault{%s}' % sciNotStr
                s = r'$%s\mathdefault{%s}$' % (sciNotStr, offsetStr)
            else:
                if self.offset:
                    sep = " + " if self.offset > 0 else " - "
                    s = sep.join((sciNotStr, offsetStr))
                else:
                    sep = ""
                s = sep.join((sciNotStr, offsetStr))

        return self.fix_minus(s)


@dataclass
class FitResult:
    s2t_best: float
    s2t_min1sigma: float
    s2t_max1sigma: float

    dm2_best: float
    dm2_min1sigma: float
    dm2_max1sigma: float


def find_lims(xs, ys, yval):
    """ Interpolate the x positions where y crosses yval. Assumes ys is concave
    up. """
    assert len(xs) == len(ys)

    def interp(i):
        return ((yval - ys[i+1]) * xs[i] + (ys[i] - yval) * xs[i+1]) / \
            (ys[i] - ys[i+1])

    xmin, xmax = xs[0], xs[-1]

    for i in range(len(ys) - 1):
        if ys[i] > yval and ys[i+1] <= yval:
            xmin = interp(i)
        elif ys[i] <= yval and ys[i+1] > yval:
            xmax = interp(i)
            break

    if xmin == xs[0]:
        print("Warning: Default xmin")
    if xmax == xs[-1]:
        print("Warning: Default xmax")

    return xmin, xmax


def read_fit_file(fname):
    f = R.TFile(fname)
    h = f.h_chi2_map

    # XXX keep this or not?
    t = f.Get("tr_fit")
    t.GetEntry(0)
    s2t_best = t.GetLeaf("s2t_min").GetValue()
    dm2_best = t.GetLeaf("dm2_min").GetValue()

    # NB: This is valid for fit results generated after Oct 27 2020
    # For older results, need (GetBinLowEdge(1), GetBinUpEdge(N))
    nS2T = h.GetNbinsX()
    nDM2 = h.GetNbinsY()
    s2t_min = h.GetXaxis().GetBinCenter(1)
    s2t_max = h.GetXaxis().GetBinCenter(nS2T)
    dm2_min = h.GetYaxis().GetBinCenter(1)
    dm2_max = h.GetYaxis().GetBinCenter(nDM2)

    chi2_map = [[h.GetBinContent(is2+1, idm+1) for is2 in range(nS2T)]
                for idm in range(nDM2)]
    chi2_map = np.array(chi2_map)

    chi2_best = chi2_map.min()

    sin22t13 = np.linspace(s2t_min, s2t_max, nS2T)
    dm2 = np.linspace(dm2_min, dm2_max, nDM2)

    def get_dChi2_s2t(is2):
        proj_chi2 = 1e10
        for idm in range(nDM2):
            if chi2_map[idm][is2] < proj_chi2:
                proj_chi2 = chi2_map[idm][is2]
        return proj_chi2 - chi2_best

    def get_dChi2_dm2(idm):
        proj_chi2 = 1e10
        for is2 in range(nS2T):
            if chi2_map[idm][is2] < proj_chi2:
                proj_chi2 = chi2_map[idm][is2]
        return proj_chi2 - chi2_best

    chi2_s2t = np.array([get_dChi2_s2t(is2) for is2 in range(nS2T)])
    chi2_dm2 = np.array([get_dChi2_dm2(idm) for idm in range(nDM2)])

    s2t_min1sigma, s2t_max1sigma = find_lims(sin22t13, chi2_s2t, 1)
    dm2_min1sigma, dm2_max1sigma = find_lims(dm2, chi2_dm2, 1)

    return FitResult(s2t_best=s2t_best,
                     s2t_min1sigma=s2t_min1sigma,
                     s2t_max1sigma=s2t_max1sigma,
                     dm2_best=dm2_best,
                     dm2_min1sigma=dm2_min1sigma,
                     dm2_max1sigma=dm2_max1sigma)


def read_study(study):
    data = []
    for direc in sorted(glob(f"fit_results/{study}/*")):
        print(direc)
        parts = direc.split("/")[-1].split("_")
        cut_pe = float(parts[-2][:-2])
        time_s = float(parts[-1][:-1])
        fit_result = read_fit_file(f"{direc}/fit_shape_2d.root")
        row = {'cut_pe': cut_pe, 'time_s': time_s, **asdict(fit_result)}
        data.append(row)
    return pd.DataFrame(data)


def read_csv(csvfile):
    "Reads what we get from df.to_csv(csvfile)"
    return pd.read_csv(csvfile, index_col=0)

# https://stackoverflow.com/questions/43525546/plotting-pcolormesh-from-filtered-pandas-dataframe-for-defined-x-y-ranges-even
def plot2d(df, expr, title, name, tag,
           title_extra=None, sciticks=True, mark_nom=True, mark_min=False,
           relative=False, offset_decimals=3,
           **kwargs):
    df = df.copy()
    df["vals"] = df.eval(expr)
    vmin, vmax = df["vals"].min(), df["vals"].max()
    piv = df.pivot_table(index="time_s", columns="cut_pe", values="vals")
    print(piv)
    global PIV
    PIV = piv

    # plt.figure(figsize=[9.6, 7.2])
    plt.figure()
    if relative:
        val_nom = piv.loc[0.375, 3e5]
        values = piv.values / val_nom - 1
    else:
        values = piv.values
    result = plt.pcolormesh(piv.columns, piv.index, values,
                            shading="nearest", **kwargs)
    cbar = plt.colorbar(format=MyScalarFormatter(offset_decimals))
    if sciticks:
        print("sciticks")
        cbar.formatter.set_powerlimits((0, 0))
    if mark_nom:
        plt.plot(3e5, 0.375, "P", markerfacecolor="red", markeredgecolor="red", ms=8)
        plt.plot(4e5, 1, "X", markerfacecolor="darkorange", markeredgecolor="darkorange", ms=8)
    if mark_min:
        min_t, min_E = piv.stack().idxmin()
        plt.plot([min_E], [min_t], "w*", ms=10)
    title_extra = f" ({title_extra})" if title_extra else ""
    if (title_extra == "") and relative:
        title_extra = " (frac. diff. from nominal)"
    plt.title(title + title_extra)
    plt.xlabel("Shower muon definition [pe]")
    plt.ylabel("Shower veto time [s]")
    # plt.xticks(piv.columns)
    plt.xticks([piv.columns[i] for i in range(0, len(piv.columns), 2)])
    plt.yticks(piv.index)
    plt.tight_layout()

    suffix = "_rel" if relative else ""
    fname = f"gfx/{tag}/{name}{suffix}.pdf"
    os.system(f"mkdir -p {os.path.dirname(fname)}")
    plt.savefig(fname)
    return result, vmin, vmax


def _plot_results(df, tag, expr, title, name, is_data=True, **kwargs):
    suffix = " (P17B data)" if is_data else " (toy MC)"
    ext = "" if is_data else "_toymc"
    if "vmax" in kwargs:
        ext += "_detail"
    return plot2d(df, expr, title + suffix, name + ext,
                  tag, **kwargs)


def plot_s2t_best(df, tag, **kwargs):
    expr = "s2t_best"
    title = r"Best-fit $\sin^2 2\theta_{13}$"
    return _plot_results(df, tag, expr, title, "s2t_best", **kwargs)


def plot_dm2_best(df, tag, **kwargs):
    expr = "dm2_best"
    title = r"Best-fit $\Delta m^2_{ee}$"
    return _plot_results(df, tag, expr, title, "dm2_best", **kwargs)


def plot_s2t_mid(df, tag, **kwargs):
    expr = "0.5 * (s2t_max1sigma + s2t_min1sigma)"
    # title = r"Middle of 1$\sigma$ range for $\sin^2 2\theta_{13}$"
    title = r"Best-fit $\sin^2 2\theta_{13}$"
    return _plot_results(df, tag, expr, title, "s2t_mid", **kwargs)


def plot_dm2_mid(df, tag, **kwargs):
    expr = "0.5 * (dm2_max1sigma + dm2_min1sigma)"
    # title = r"Middle of 1$\sigma$ range for $\Delta m^2_{ee}$"
    title = r"Best-fit $\Delta m^2_{ee}$"
    return _plot_results(df, tag, expr, title, "dm2_mid", **kwargs)


def plot_s2t_unc(df, tag, **kwargs):
    expr = "0.5 * (s2t_max1sigma - s2t_min1sigma)"
    title = r"1$\sigma$ uncertainty on $\sin^2 2\theta_{13}$"
    return _plot_results(df, tag, expr, title, "s2t_unc", **kwargs)


def plot_dm2_unc(df, tag, **kwargs):
    expr = "0.5 * (dm2_max1sigma - dm2_min1sigma)"
    title = r"1$\sigma$ uncertainty on $\Delta m^2_{ee}$"
    return _plot_results(df, tag, expr, title, "dm2_unc", **kwargs)


def plot_all(tag, offset_decimals=[1, 3], **kwargs):
    df = read_csv(f"summaries/{tag}.csv")
    # plot_s2t_best(df, tag)
    # plot_dm2_best(df, tag)
    # plot_s2t_unc(df, tag)
    # plot_dm2_unc(df, tag)
    plot_s2t_mid(df, tag, offset_decimals=offset_decimals[0], **kwargs)
    plot_dm2_mid(df, tag, offset_decimals=offset_decimals[1], **kwargs)


def plot_unc_all(tag, offset_decimals=[4, 4], detail=False, vmax=None, **kwargs):
    kwargs.setdefault("mark_min", True)
    df = read_csv(f"summaries/{tag}.csv")
    kwargs_s2t = {"offset_decimals": offset_decimals[0], **kwargs}
    kwargs_dm2 = {"offset_decimals": offset_decimals[1], **kwargs}
    if vmax:
        kwargs_s2t["vmax"] = vmax[0]
        kwargs_dm2["vmax"] = vmax[1]
    plot_s2t_unc(df, tag, **kwargs_s2t)
    plot_dm2_unc(df, tag, **kwargs_dm2)


def plot_all_all(**kwargs):
    for tag in ["oct20_data_bcw", "oct20_data", "oct20_yolo3_bcw",
                "oct20_yolo3_truePars_bcw", "oct20_yolo3_truePars"]:
        plot_all(tag, **kwargs)


def detno(hall, det):
    return 1 + (hall-1)*2 + det-1


@lru_cache()
def read_quantity(tag, qty, nADs=8):
    return read_csv(f"summaries/{tag}.{qty}.{nADs}ad.csv")


def do_plot2d_quantity(df, tag, quantity, title, hall, det, is_data, nADs=8,
                       **kwargs):
    what = "data" if is_data else "toy"
    what = f"{nADs}AD {what}" if nADs != -1 else what
    prd_name = f"{nADs}ad" if nADs != -1 else "sum"
    suffix = "_toymc" if not is_data else ""
    if det == -1:
        loc_name = f"EH{hall}"
        loc_name2 = f"eh{hall}"
        if hall == 1:
            expr = "AD1 + AD2"
        elif hall == 2:
            expr = "AD3 + AD4"
        elif hall == 3:
            expr = "AD5 + AD6 + AD7 + AD8"
        elif hall == 12:
            expr = "AD1 + AD2 + AD3 + AD4"
        elif hall == 42:
            loc_name = "Far/Near"
            loc_name2 = "farOverNear"
            expr = "(AD5 + AD6 + AD7 + AD8)/(AD1 + AD2 + AD3 + AD4)"
    else:
        loc_name = f"EH{hall}-AD{det}"
        loc_name2 = f"eh{hall}_ad{det}"
        n = detno(hall, det)
        expr = f"AD{n}"
    return plot2d(df, expr, f"{title}, {loc_name} ({what})",
                  f"{quantity}.{loc_name2}.{prd_name}{suffix}", tag, **kwargs)


def plot2d_quantity(tag, quantity, title, hall, det, is_data, nADs=8,
                    **kwargs):
    df = read_quantity(tag, quantity, nADs)
    return do_plot2d_quantity(df, tag, quantity, title, hall, det, is_data, nADs,
                              **kwargs)


def plot_veto_eff(tag, hall, det, is_data, nADs=8, **kwargs):
    return plot2d_quantity(tag, "veto_eff", "Muon veto efficiency",
                           hall, det, is_data, nADs, **kwargs)


def plot_mult_eff(tag, hall, det, is_data, nADs=8, **kwargs):
    return plot2d_quantity(tag, "mult_eff", "Mult cut efficiency",
                           hall, det, is_data, nADs, **kwargs)


def plot_li9_bkg(tag, hall, det, is_data, nADs=8, **kwargs):
    return plot2d_quantity(tag, "li9_bkg", r"Daily $^9$Li rate",
                           hall, det, is_data, nADs, **kwargs)


def plot_tot_bkg(tag, hall, det, is_data, nADs=8, **kwargs):
    return plot2d_quantity(tag, "tot_bkg", r"Daily bkg rate",
                           hall, det, is_data, nADs, **kwargs)


def plot_obs_evt(tag, hall, det, is_data, nADs=8, **kwargs):
    return plot2d_quantity(tag, "obs_evt", "# of IBD candidates",
                           hall, det, is_data, nADs, **kwargs)


def plot_spec_int(tag, hall, det, is_data, nADs=8, **kwargs):
    return plot2d_quantity(tag, "spec_int", "IBD spectrum integral",
                           hall, det, is_data, nADs, **kwargs)


# def plot_bkg_over_tot(tag, hall, det, is_data, nADs=8, **kwargs):
#     df_bkg = read_quantity(tag, "tot_bkg", nADs)
#     df_spec = read_quantity(tag, "spec_int", nADs)


def plot_spec_int_sum_effCorr(tag, hall, is_data, **kwargs):
    dfs = {}

    for nADs in [6, 8, 7]:
        df_veto = read_quantity(tag, "veto_eff", nADs).set_index(["cut_pe", "time_s"])
        df_mult = read_quantity(tag, "mult_eff", nADs).set_index(["cut_pe", "time_s"])
        df_spec_int = read_quantity(tag, "spec_int", nADs).set_index(["cut_pe", "time_s"])
        dfs[nADs] = df_spec_int / df_veto / df_mult
        dfs[nADs] = dfs[nADs].fillna(0)

    df = dfs[6] + dfs[8] + dfs[7]

    return do_plot2d_quantity(df.reset_index(), tag, "spec_int_sum_effCorr",
                              "Eff-corr raw spectrum", hall, -1, is_data,
                              nADs=-1, **kwargs)

def plot_spec_int_effCorr(tag, hall, is_data, nADs=8, **kwargs):
    df_veto = read_quantity(tag, "veto_eff", nADs).set_index(["cut_pe", "time_s"])
    df_mult = read_quantity(tag, "mult_eff", nADs).set_index(["cut_pe", "time_s"])
    df_spec_int = read_quantity(tag, "spec_int", nADs).set_index(["cut_pe", "time_s"])
    df = df_spec_int / df_veto / df_mult
    df = df.fillna(0)

    return do_plot2d_quantity(df.reset_index(), tag, "spec_int_effCorr",
                              "Eff-corr raw spectrum", hall, -1, is_data,
                              nADs=nADs, **kwargs)


def plot_all_quantities(same_scale=False):
    for func in [plot_veto_eff, plot_li9_bkg, plot_spec_int]:
        for hall, det in [(1, 1), (3, 1)]:
            _, min1, max1 = func("fine", hall, det, True)
            _, min2, max2 = func("fine_toymc", hall, det, False)
            if same_scale:
                vmin = min(min1, min2)
                vmax = max(max1, max2)
                func("fine", hall, det, True, vmin=vmin, vmax=vmax)
                func("fine_toymc", hall, det, False, vmin=vmin, vmax=vmax)


def plot_all_fits(same_scale=False):
    df_data = read_csv("summaries/fine.csv")
    df_toy = read_csv("summaries/fine_toymc.csv")
    for func in [plot_s2t_mid, plot_dm2_mid,
                 plot_s2t_best, plot_dm2_best,
                 plot_s2t_unc, plot_dm2_unc]:
        _, min1, max1 = func(df_data, "fine")
        _, min2, max2 = func(df_toy, "fine_toymc")
        if same_scale:
            vmin = min(min1, min2)
            vmax = max(max1, max2)
            func(df_data, "fine", vmin=vmin, vmax=vmax)
            func(df_toy, "fine_toymc", vmin=vmin, vmax=vmax)
