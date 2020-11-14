from glob import glob
import os

import ROOT as R
from numpy import format_float_scientific as fmt


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

    c.cd(1)
    title = f"Data: {cut_pe:.2g} pe, {time_s:.3g} s (EH3/EH1)"
    h_null, *_ = overlay_spectra(f_data, -1, 1, 0, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    c.cd(3)
    title = f"Data: {cut_pe:.2g} pe, {time_s:.3g} s (EH3/EH2)"
    h_null, *_ = overlay_spectra(f_data, -1, 1, 1, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    c.cd(2)
    title = f"Toy: {cut_pe:.2g} pe, {time_s:.3g} s (EH3/EH1)"
    h_null, *_ = overlay_spectra(f_toy, -1, 1, 0, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    c.cd(4)
    title = f"Toy: {cut_pe:.2g} pe, {time_s:.3g} s (EH3/EH2)"
    h_null, *_ = overlay_spectra(f_toy, -1, 1, 1, title)
    h_null.GetYaxis().SetRangeUser(0, 22)
    R.gPad.Modified()

    return c


def overlay_4x4_all():
    os.system("mkdir -p gfx/overlay_4x4")
    for path in glob("fit_results/oct20_data/*"):
        cutname = os.path.basename(path)
        c = overlay_4x4(cutname)
        c.SaveAs(f"gfx/overlay_4x4/overlay_4x4_{cutname}.png")


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
