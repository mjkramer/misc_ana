from glob import glob
import os

import ROOT as R
from numpy import format_float_scientific


# because automatic memory management is always soooooo helpful
def keep(o):
    R.SetOwnership(o, False)     # don't delete it, python!
    try:
        o.SetDirectory(R.gROOT)  # don't delete it, root!
        # o.SetDirectory(0)
    except Exception:
        pass                     # unless you weren't going to anyway
    return o


def kept(o):
    keep(o)
    return o


def overlay_4x4(cutname):
    parts = cutname.split("_")
    cut_pe = float(parts[0][:-2])
    time_s = float(parts[1][:-1])

    c = kept(R.TCanvas(f"c_{cutname}", f"c_{cutname}", 1400, 1000))
    c.Divide(2, 2)

    # keep?
    f_data = R.TFile(f"fit_results/oct20_data/{cutname}/fit_shape_2d.root")
    f_toy = R.TFile(f"fit_results/oct20_yolo3/{cutname}/fit_shape_2d.root")

    cut_pe_str = format_float_scientific(cut_pe, exp_digits=1)

    c.cd(1)
    title = f"Data: {cut_pe_str} pe, {time_s:.3g} s (EH3/EH1)"
    h_null, *_ = overlay_spectra(f_data, -1, 1, 0, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    c.cd(3)
    title = f"Data: {cut_pe_str} pe, {time_s:.3g} s (EH3/EH2)"
    h_null, *_ = overlay_spectra(f_data, -1, 1, 1, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    c.cd(2)
    title = f"Toy: {cut_pe_str} pe, {time_s:.3g} s (EH3/EH1)"
    h_null, *_ = overlay_spectra(f_toy, -1, 1, 0, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    c.cd(4)
    title = f"Toy: {cut_pe_str} pe, {time_s:.3g} s (EH3/EH2)"
    h_null, *_ = overlay_spectra(f_toy, -1, 1, 1, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    return c


def overlay_4x4_all():
    os.system("mkdir -p gfx/overlay_4x4")
    for path in glob("fit_results/oct20_data/*"):
        cutname = os.path.basename(path)
        c = overlay_4x4(cutname)
        c.SaveAs(f"gfx/overlay_4x4/overlay_4x4_{fix_cutname(cutname)}.png")


def overlay_spectra(f, istage, imode, ipred, title):
    stagename = "sum" if istage == -1 else f"stage{istage}"
    h_obs = kept(f.Get(f"h_final_obs_{stagename}_mode{imode}_{ipred}"))
    h_pred = kept(f.Get(f"h_final_pred_{stagename}_mode{imode}_{ipred}"))
    h_null = kept(f.Get(f"h_final_pred_null_{stagename}_mode{imode}_{ipred}"))
    # h_nom = kept(f.Get(f"h_final_pred_nom_{stagename}_mode{imode}_{ipred}"))

    # print(h_obs.GetFillStyle(), h_pred.GetFillStyle(), h_null.GetFillStyle(), h_nom.GetFillStyle())

    R.gStyle.SetTitleX(0.5)
    R.gStyle.SetTitleY(0.98)
    R.gStyle.SetTitleAlign(23)

    # h_nom.SetLineColor(R.kGreen)
    # h_nom.SetLineWidth(2)
    # h_nom.SetLineStyle(2)

    h_pred.SetFillStyle(0)
    h_pred.SetLineStyle(1)
    h_pred.SetLineWidth(2)

    h_null.SetLineColor(R.kMagenta)
    h_null.SetLineWidth(2)
    h_null.SetLineStyle(9)

    h_obs.SetMarkerStyle(20)
    h_obs.SetMarkerSize(0.7)

    ratio = h_obs.GetTitle()

    # h_null.SetTitle(f"{title} ({ratio})")
    # can = kept(R.TCanvas())
    h_null.Draw("hist")
    # h_nom.Draw("hist same")
    h_pred.Draw("hist same")
    h_obs.Draw("same")

    h_null.SetTitle("Null pars")
    # h_nom.SetTitle("Nominal pars")
    h_pred.SetTitle("Best pars")
    h_obs.SetTitle("Observed")

    # can.BuildLegend(0.3, 0.21, 0.3, 0.21, "", "L")
    leg = kept(R.TLegend(0.65, 0.65, 0.88, 0.88))
    leg.AddEntry(h_obs, "", "P")
    leg.AddEntry(h_pred, "", "L")
    # leg.AddEntry(h_nom, "", "L")
    leg.AddEntry(h_null, "", "L")
    leg.SetBorderSize(0)
    leg.Draw()

    # h_null.SetTitle(f"{title} ({ratio})")
    h_null.SetTitle(title)
    h_null.GetXaxis().SetLabelSize(0.04)
    h_null.GetXaxis().SetTitle("Energy [MeV]")
    h_null.GetYaxis().SetLabelSize(0.04)
    h_null.GetYaxis().SetTitle("Entries / bin / liveday")
    R.gStyle.SetTitleX(0.5)
    R.gStyle.SetTitleAlign(23)

    # can.Draw()
    R.gStyle.SetTitleX(0.5)
    R.gStyle.SetTitleAlign(23)

    R.gPad.Modified()
    R.gPad.Update()
    # return h_null, h_nom, h_pred, h_obs
    return h_null, h_pred, h_obs


def get_eprompt_shapes(study, cutname):
    hists = [None, None, None]
    for nADs in [6, 8, 7]:
        f = R.TFile(f"fit_results/{study}/{cutname}/ibd_eprompt_shapes_{nADs}ad.root")
        for hall in [1, 2, 3]:
            for det in [1, 2, 3, 4] if hall == 3 else [1, 2]:
                h = f.Get(f"h_ibd_eprompt_inclusive_eh{hall}_ad{det}")
                if hists[hall-1] is None:
                    hists[hall-1] = kept(h.Clone(f"h_eh{hall}"))
                else:
                    hists[hall-1].Add(h)
    return hists


def compare_obs_3x2(cutname, fudge=False):
    R.gStyle.SetOptStat(0)

    # reactor anti-nu anomaly
    # we got this from toy/data spectra integral ratios between data and toy
    # for 3e5 pe, 0.5 s (close to the nominal 3e5 / 0.4004)
    # [eh1, eh2, eh3] = [1.057797, 1.057343, 1.057637]
    magicFudge = 1.0576
    fudgeness = " (fudged)" if fudge else ""

    parts = cutname.split("_")
    cut_pe = float(parts[0][:-2])
    time_s = float(parts[1][:-1])
    cut_pe_str = format_float_scientific(cut_pe, exp_digits=1)

    c = kept(R.TCanvas(f"c_obs_{cutname}{fudgeness}", f"c_obs_{cutname}{fudgeness}",
                       1820, 1300))
    c.Divide(3, 2)

    hs_data = get_eprompt_shapes("oct20_data", cutname)
    hs_toy = get_eprompt_shapes("oct20_yolo3", cutname)

    for hall in [1, 2, 3]:
        if fudge:
            hs_data[hall-1].Scale(magicFudge)

        c.cd(hall)
        basetitle = f"{cut_pe_str} pe, {time_s:.3g} s: EH{hall}"
        hs_data[hall-1].SetTitle(f"{basetitle}{fudgeness}")
        hs_data[hall-1].SetLineColor(R.kRed)
        hs_toy[hall-1].SetLineColor(R.kBlue)
        hs_data[hall-1].Draw("hist")
        hs_toy[hall-1].Draw("hist same")
        ymax = max(hs_data[hall-1].GetMaximum(),
                   hs_toy[hall-1].GetMaximum())
        hs_data[hall-1].GetYaxis().SetRangeUser(0, 1.1 * ymax)
        leg = kept(R.TLegend(0.77, 0.80, 0.88, 0.88))
        leg.AddEntry(hs_data[hall-1], "Data", "L")
        leg.AddEntry(hs_toy[hall-1], "Toy", "L")
        leg.SetBorderSize(0)
        leg.Draw()
        R.gPad.Modified()
        R.gPad.Update()

        c.cd(hall + 3)
        hdatnorm = kept(hs_data[hall-1].Clone())
        htoynorm = kept(hs_toy[hall-1].Clone())
        hdatnorm.Scale(1./hdatnorm.Integral())
        htoynorm.Scale(1./htoynorm.Integral())
        hdatnorm.SetTitle(basetitle + " (normalized)")
        hdatnorm.Draw("hist")
        htoynorm.Draw("hist same")
        ymax = max(hdatnorm.GetMaximum(),
                   htoynorm.GetMaximum())
        hdatnorm.GetYaxis().SetRangeUser(0, 1.1 * ymax)
        leg = kept(R.TLegend(0.77, 0.80, 0.88, 0.88))
        leg.AddEntry(hdatnorm, "Data", "L")
        leg.AddEntry(htoynorm, "Toy", "L")
        leg.SetBorderSize(0)
        leg.Draw()
        R.gPad.Modified()
        R.gPad.Update()

    return c


def compare_obs_3x2_all(fudge=False):
    fudgeness = "_fudge" if fudge else ""
    os.system(f"mkdir -p gfx/compare_obs_3x2{fudgeness}")
    for path in glob("fit_results/oct20_data/*"):
        cutname = os.path.basename(path)
        c = compare_obs_3x2(cutname, fudge=fudge)
        c.SaveAs(f"gfx/compare_obs_3x2{fudgeness}/compare_obs_3x2{fudgeness}_{fix_cutname(cutname)}.png")


def fix_cutname(cutname):
    "Ensure all time_s have 3 sig figs so that the names sort properly"
    parts = cutname.split("_")
    cut_pe = float(parts[0][:-2])
    time_s = float(parts[1][:-1])
    return f"{cut_pe:6.1f}pe_{time_s:1.2f}s"


def plot_the_bump(cutname):
    R.gStyle.SetOptStat(0)
    R.TH1.SetDefaultSumw2(True)

    hs_data = get_eprompt_shapes("oct20_data", cutname)
    hs_toy = get_eprompt_shapes("oct20_yolo3", cutname)

    c = kept(R.TCanvas(f"c_bump_{cutname}", f"c_bump_{cutname}",
                       1820, 650))
    c.Divide(3, 1)

    for hall in [1, 2, 3]:
        c.cd(hall)
        hs_data[hall-1].Scale(1./hs_data[hall-1].Integral())
        hs_toy[hall-1].Scale(1./hs_toy[hall-1].Integral())
        hs_data[hall-1].Divide(hs_toy[hall-1])
        hs_data[hall-1].SetTitle(f"Data / toy (EH{hall})")
        hs_data[hall-1].Draw("hist")

    return c
