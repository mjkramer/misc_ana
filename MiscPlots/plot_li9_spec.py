import os

import ROOT as R

from util import keep


PRED_SPEC = "/global/homes/m/mkramer/mywork/ThesisAnalysis/Fitter/li9_spectrum/8he9li_nominal_spectrum.root"
MEAS_SPEC =  "/global/homes/m/mkramer/mywork/ThesisAnalysis/li9he8/Li9Spectrum.root"


def plot_li9_spec():
    gfxdir = "gfx/li9_spec"
    os.system(f"mkdir -p {gfxdir}")

    f_pred = R.TFile(PRED_SPEC)
    h_pred = keep(f_pred.Get("h_nominal").Clone("h_pred"))
    h_pred.SetTitle("Li9 spectrum")
    h_pred.SetXTitle("MeV")
    h_pred.Scale(1/h_pred.Integral("width"))

    f_meas = R.TFile(MEAS_SPEC)
    h_meas = keep(f_meas.Get("EH1_Li9").Clone("h_meas"))
    h_meas.Reset()
    for hall in [1, 2, 3]:
        h = f_meas.Get(f"EH{hall}_Li9")
        h_meas.Add(h)
    h_meas.Scale(1/h_meas.Integral("width"))

    c = keep(R.TCanvas())
    h_pred.Draw("HIST")
    h_meas.Draw("SAME")
    h_pred.GetYaxis().SetRangeUser(0, 0.18)
    R.gPad.Modified()
    R.gPad.Update()

    c.SaveAs(f"{gfxdir}/li9_spec.pdf")
    c.SaveAs(f"{gfxdir}/li9_spec.png")
