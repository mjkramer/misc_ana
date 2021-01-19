from glob import glob
import os

import ROOT as R

from diagnostics_ROOT import get_corrspecs, get_eprompt_shapes
from util import keep


R.gStyle.SetOptStat(0)


def mev2coloridx(mev):
    mev_min, mev_max = 4, 7
    frac = (mev - mev_min) / (mev_max - mev_min)
    return R.TColor.GetPalette()[int(frac * 254)]


def plot_extrap_mishmash(study, ipred):
    R.gStyle.SetTitleY(0.98)
    R.gStyle.SetPalette(R.kViridis)

    nearname = "EH2" if ipred == 1 else "EH1"

    h0 = None
    ymin = 1000
    ymax = -1000

    dirs = glob(f"fit_results/{study}/*MeV")
    for i, direc in enumerate(sorted(dirs)):
        print(direc)
        mev = float(os.path.basename(direc)[:-3])
        f = R.TFile(f"{direc}/fit_shape_2d.root")
        h_obs = f.Get(f"h_final_obs_sum_mode1_{ipred}")
        h_obs = keep(h_obs.Clone("my_" + h_obs.GetName()))
        h_nom = keep(f.Get(f"h_final_pred_nom_sum_mode1_{ipred}"))
        h_obs.Divide(h_nom)
        # for binno in range(1, h_obs.GetNbinsX()+1):
        #     h_obs.SetBinError(binno, 0.00001)
        h_obs.SetMarkerColor(mev2coloridx(mev))
        h_obs.SetLineColor(mev2coloridx(mev))
        h_obs.SetMarkerStyle(20)
        h_obs.SetMarkerSize(0.7)
        h_obs.GetXaxis().SetLabelSize(0.04)
        h_obs.GetYaxis().SetLabelSize(0.04)
        h_obs.SetYTitle("")
        if h0 is None:
            h0 = h_obs
            h_obs.SetTitle(f"Ratio of EH3 data to nominal {nearname} pred")
            h_obs.Draw()
        else:
            h_obs.Draw("SAME")
        ymin = min(ymin, h_obs.GetMinimum())
        ymax = max(ymax, h_obs.GetMaximum())

    h0.GetYaxis().SetRangeUser(0.9 * ymin, 1.1 * ymax)


def plot_extrap_mishmash_both(study):
    cname = f"c_extrap_mish_{study}"
    c = keep(R.TCanvas(cname, cname, 1400, 500))
    c.Divide(2, 1)

    c.cd(1)
    plot_extrap_mishmash(study, 0)
    c.cd(2)
    plot_extrap_mishmash(study, 1)

    os.system("mkdir -p gfx/extrap_mishmash")
    c.SaveAs(f"gfx/extrap_mishmash/extrap_mishmash.{study}.png")


def plot_contour_grid(study):
    R.gStyle.SetOptStat(0)

    nrows, ncols = 4, 4
    ncells = nrows * ncols
    cans = []

    outdir = f"gfx/contgrid/{study}"
    os.system(f"mkdir -p {outdir}")

    dirs = glob(f"fit_results/{study}/*MeV")
    for i, direc in enumerate(sorted(dirs)):
        ican = i // ncells
        icell = i % ncells
        # row = 1 + icell // ncols
        # col = 1 + icell % ncols

        if icell == 0:
            cname = f"c_cont_grid{ican}"
            c = keep(R.TCanvas(cname, cname, 1400, 1000))
            c.Divide(nrows, ncols)
            cans.append(c)

        cans[-1].cd(1 + icell)

        f = keep(R.TFile(f"{direc}/fit_shape_2d.root"))
        h = keep(f.h_chi2_map)
        for ax in [h.GetXaxis(), h.GetYaxis()]:
            ax.SetLabelSize(0.04)
        h.SetTitle(os.path.basename(direc))
        R.gPad.SetLogz()
        h.Draw("COLZ")

        if icell == ncells - 1:
            cans[-1].SaveAs(f"{outdir}/contgrid_{ican}.png")

    cans[-1].SaveAs(f"{outdir}/contgrid_{len(cans)-1}.png")


def plot_func_mishmash(study, name, func, *args, **kwargs):
    R.gStyle.SetTitleY(0.98)
    R.gStyle.SetPalette(R.kViridis)

    cname = f"c_{name}_mish_{study}"
    c = keep(R.TCanvas(cname, cname, 1820, 650))
    c.Divide(3, 1)

    dirs = glob(f"fit_results/{study}/*MeV")
    for i, direc in enumerate(sorted(dirs)):
        cutname = os.path.basename(direc)
        mev = float(cutname[:-3])
        hists = func(study, cutname, *args, **kwargs)
        for hall in [1, 2, 3]:
            c.cd(hall)
            opt = "hist" + (" same" if i != 0 else "")
            hists[hall-1].SetLineColor(mev2coloridx(mev))
            hists[hall-1].SetTitle(f"{name} (EH{hall})")
            hists[hall-1].Draw(opt)

    os.system(f"mkdir -p gfx/{name}_mishmash")
    c.SaveAs(f"gfx/{name}_mishmash/{name}_mishmash.{study}.png")


def plot_obs_evts_mishmash(study):
    plot_func_mishmash(study, "obs_evts", get_eprompt_shapes)


def plot_corr_evts_mishmash(study):
    plot_func_mishmash(study, "corr_evts", get_corrspecs, "IBD")
