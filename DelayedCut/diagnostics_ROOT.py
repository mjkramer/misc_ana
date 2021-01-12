from glob import glob
import os

import ROOT as R

from util import keep

# R.gROOT.SetBatch(True)


def dump_contours(study):
    for subdir in ["norm", "log"]:
        os.system(f"mkdir -p gfx/contours/{study}/{subdir}")

    for cutdir in sorted(glob(f"fit_results/{study}/*")):
        f = R.TFile(f"{cutdir}/fit_shape_2d.root")
        h_chi2 = f.h_chi2_map
        for ax in [h_chi2.GetXaxis(), h_chi2.GetYaxis()]:
            ax.SetLabelSize(0.04)
        cutname = os.path.basename(cutdir)
        h_chi2.SetTitle(cutname)
        c = R.TCanvas()
        h_chi2.Draw("COLZ")
        c.SaveAs(f"gfx/contours/{study}/norm/{cutname}.png")
        c.SetLogz()
        c.SaveAs(f"gfx/contours/{study}/log/{cutname}.png")


# -----------------------------------------------------------------------------


def gen_all(func, name, study, tag=None):
    tag = name if tag is None else tag
    gfxdir = f"gfx/{name}/{study}"
    os.system(f"mkdir -p {gfxdir}")
    for cutdir in glob(f"fit_results/{study}/*"):
        cutname = os.path.basename(cutdir)
        c = func(study, cutname)
        c.SaveAs(f"{gfxdir}/{tag}_{cutname}.png")


# -----------------------------------------------------------------------------


def overlay_spectra(f, istage, imode, ipred, title):
    stagename = "sum" if istage == -1 else f"stage{istage}"
    h_obs = keep(f.Get(f"h_final_obs_{stagename}_mode{imode}_{ipred}"))
    h_pred = keep(f.Get(f"h_final_pred_{stagename}_mode{imode}_{ipred}"))
    h_null = keep(f.Get(f"h_final_pred_null_{stagename}_mode{imode}_{ipred}"))
    h_nom = keep(f.Get(f"h_final_pred_nom_{stagename}_mode{imode}_{ipred}"))

    R.gStyle.SetTitleX(0.5)
    R.gStyle.SetTitleY(0.98)
    R.gStyle.SetTitleAlign(23)

    h_nom.SetLineColor(R.kGreen)
    h_nom.SetLineWidth(2)
    h_nom.SetLineStyle(2)

    h_pred.SetFillStyle(0)
    h_pred.SetLineStyle(1)
    h_pred.SetLineWidth(2)

    h_null.SetLineColor(R.kMagenta)
    h_null.SetLineWidth(2)
    h_null.SetLineStyle(9)

    h_obs.SetMarkerStyle(20)
    h_obs.SetMarkerSize(0.7)

    # ratio = h_obs.GetTitle()

    # h_null.SetTitle(f"{title} ({ratio})")
    # can = keep(R.TCanvas())
    h = h_null                  # First one we draw; owns the axes etc.
    h_null.Draw("hist")
    h_nom.Draw("hist same")
    h_pred.Draw("hist same")
    h_obs.Draw("same")

    h_null.SetTitle("Null pars")
    h_nom.SetTitle("Nominal pars")
    h_pred.SetTitle("Best pars")
    h_obs.SetTitle("Observed")

    # can.BuildLegend(0.3, 0.21, 0.3, 0.21, "", "L")
    leg = keep(R.TLegend(0.65, 0.65, 0.88, 0.88))
    leg.AddEntry(h_obs, "", "P")
    leg.AddEntry(h_pred, "", "L")
    leg.AddEntry(h_nom, "", "L")
    leg.AddEntry(h_null, "", "L")
    leg.SetBorderSize(0)
    leg.Draw()

    # h.SetTitle(f"{title} ({ratio})")
    h.SetTitle(title)
    h.GetXaxis().SetLabelSize(0.04)
    h.GetXaxis().SetTitle("Energy [MeV]")
    h.GetYaxis().SetLabelSize(0.04)
    h.GetYaxis().SetTitle("Entries / bin / liveday")
    R.gStyle.SetTitleX(0.5)
    R.gStyle.SetTitleAlign(23)
    R.gStyle.SetTitleX(0.5)
    R.gStyle.SetTitleAlign(23)

    R.gPad.Modified()
    R.gPad.Update()
    return h_null, h_nom, h_pred, h_obs


def overlay_2x1(study, cutname):
    cname = f"c_{study}_{cutname}"
    c = keep(R.TCanvas(cname, cname, 1400, 500))
    c.Divide(2, 1)

    f = R.TFile(f"fit_results/{study}/{cutname}/fit_shape_2d.root")

    def overlay(*args):
        h, *_ = overlay_spectra(*args)
        h.GetYaxis().SetRangeUser(0, 22)
        R.gPad.Modified()

    c.cd(1)
    title = f"{cutname}, EH3/EH1"
    overlay(f, -1, 1, 0, title)

    c.cd(2)
    title = f"{cutname}, EH3/EH2"
    overlay(f, -1, 1, 1, title)

    return c


def overlay_2x1_all(study):
    gen_all(overlay_2x1, "overlay", study)


# -----------------------------------------------------------------------------


def get_eprompt_shapes(study, cutname):
    hists = [None, None, None]
    for nADs in [6, 8, 7]:
        f = R.TFile(f"fit_results/{study}/{cutname}/" +
                    f"ibd_eprompt_shapes_{nADs}ad.root")
        for hall in [1, 2, 3]:
            for det in [1, 2, 3, 4] if hall == 3 else [1, 2]:
                h = f.Get(f"h_ibd_eprompt_inclusive_eh{hall}_ad{det}")
                if hists[hall-1] is None:
                    hists[hall-1] = keep(h.Clone(f"h_eh{hall}"))
                else:
                    hists[hall-1].Add(h)
    return hists


# -----------------------------------------------------------------------------


def func_3x1(study, cutname, func=get_eprompt_shapes, desc="obs"):
    R.gStyle.SetOptStat(0)

    cname = f"c_{desc}_{study}_{cutname}"
    c = keep(R.TCanvas(cname, cname, 1820, 650))
    c.Divide(3, 1)

    hists = func(study, cutname)

    for hall in [1, 2, 3]:
        c.cd(hall)
        hists[hall-1].SetTitle(f"{cutname}, EH{hall}")
        hists[hall-1].Draw("HIST")
        R.gPad.Modified()
        R.gPad.Update()

    return c


# -----------------------------------------------------------------------------


def obs_3x1(study, cutname):
    return func_3x1(study, cutname, get_eprompt_shapes, "obs")


def obs_3x1_all(study):
    gen_all(obs_3x1, "obs", study)


# -----------------------------------------------------------------------------


def get_corrspecs(study, cutname, specname="IBD"):
    if specname == "TotBkg":
        return get_totbkg(study, cutname)

    suffix = "" if specname == "IBD" else "Spec"
    hists = [None, None, None]
    f = R.TFile(f"fit_results/{study}/{cutname}/fit_shape_2d.root")
    for istage in range(3):
        for hall in [1, 2, 3]:
            for det in [1, 2, 3, 4] if hall == 3 else [1, 2]:
                detno = 2*(hall-1) + det
                h = f.Get(f"Corr{specname}Evts{suffix}" +
                          f"_stage{istage}_AD{detno}")
                if hists[hall-1] is None:
                    name = f"h_{specname}_{study}_{cutname}_eh{hall}"
                    hists[hall-1] = keep(h.Clone(name))
                else:
                    hists[hall-1].Add(h)
    return hists


def get_totbkg(study, cutname):
    result = [None, None, None]

    for bkg in ["Acc", "Li9", "Amc", "Fn", "Aln"]:
        hists = get_corrspecs(study, cutname, specname=bkg)
        for hall in [1, 2, 3]:
            if result[hall-1] is None:
                name = f"h_TotBkg_{study}_{cutname}_eh{hall}"
                result[hall-1] = keep(hists[hall-1].Clone(name))
            else:
                result[hall-1].Add(hists[hall-1])

    return result


def corrspec_3x1(study, cutname, specname="IBD"):
    def func(study, cutname):
        return get_corrspecs(study, cutname, specname)
    return func_3x1(study, cutname, func, f"corrspec_{specname}")


def corrspec_3x1_all(study, specname="IBD"):
    def func(study, cutname):
        return corrspec_3x1(study, cutname, specname)
    name = f"corrspec_{specname}"
    gen_all(func, name, study)


def corrspec_3x1_all_all(study):
    for specname in ["IBD", "Acc", "Li9", "Amc", "Fn", "Aln", "TotBkg"]:
        corrspec_3x1_all(study, specname)
