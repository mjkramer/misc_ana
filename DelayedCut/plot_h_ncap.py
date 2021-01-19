#!/usr/bin/env python3

# This has been incorporated into IbdSel/fit_prep/get_ncap_spec.py

import os
import sys

import ROOT as R

from fudge_acc import det_active, dets_for  # XXX move to util
from util import keep, read_theta13_file


def stage2_file(nADs, site):
    return "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/data" + \
        f"/stage2_pbp/2020_01_26@del4MeV/stage2.pbp.eh{site}.{nADs}ad.root"


def theta13_file(nADs):
    return "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data" + \
        f"/fit_input/2020_01_26@del4MeV/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"


def idet(site, det):
    return (site-1)*2 + (det-1)


def get_h_ncap(nADs, site, det):
    f = R.TFile(stage2_file(nADs, site))
    R.gROOT.cd()
    hname = f"h_ncap_{nADs}ad_eh{site}_ad{det}"
    htitle = f"N-capture spectrum, EH{site}-AD{det} ({nADs}AD)"
    h_ncap = keep(R.TH1F(hname, htitle, 160, 4, 12))
    tree = f.Get(f"ibd_AD{det}")
    tree.Draw(f"eD>>{hname}", "", "goff")

    h_sing_orig = f.Get(f"h_single_AD{det}")
    h_sing = keep(h_ncap.Clone(hname.replace("ncap", "sing")))
    h_sing.Reset()

    for xbin in range(h_sing_orig.FindBin(4), h_sing_orig.FindBin(12)+1):
        h_sing.Fill(h_sing_orig.GetBinCenter(xbin),
                    h_sing_orig.GetBinContent(xbin))

    h_sing.Scale(1/h_sing.Integral())

    t13f = read_theta13_file(theta13_file(nADs))
    i = idet(site, det)

    eff_mu = t13f["veto_eff"][i]
    eff_dmc = t13f["mult_eff"][i]
    livetime = t13f["livetime"][i]
    acc_daily = t13f["acc_bkg"][i]

    h_ncap_sub = keep(h_ncap.Clone(hname.replace("ncap", "ncap_sub")))

    total_acc = acc_daily * livetime * eff_mu * eff_dmc
    h_sing.Scale(total_acc)
    h_ncap_sub.Add(h_sing, -1)

    return h_ncap, h_sing, h_ncap_sub


def plot_h_ncap(nADs, site, det, log=False):
    R.gStyle.SetOptStat(0)

    h_ncap, h_sing, h_ncap_sub = get_h_ncap(nADs, site, det)

    h_ncap.SetLineColor(R.kBlue)
    h_sing.SetLineColor(R.kRed)
    h_ncap_sub.SetLineColor(R.kMagenta)

    cname = "c_" + ("log_" if log else "") + h_ncap.GetName()[2:]
    c = keep(R.TCanvas(cname, cname))

    h_ncap.Draw("hist")
    h_sing.Draw("hist same")
    h_ncap_sub.Draw("hist same")

    oldtitle = h_ncap.GetTitle()
    h_ncap.SetTitle("raw")
    h_sing.SetTitle("acc")
    h_ncap_sub.SetTitle("raw - acc")

    if log:
        c.SetLogy()

    c.BuildLegend(0.2, 0.2, 0.2, 0.2)

    h_ncap.SetTitle(oldtitle)

    return c


def plot_h_ncap_all():
    gfxdir = "gfx/ncap"
    gfxdir_norm = f"{gfxdir}/norm"
    gfxdir_log = f"{gfxdir}/log"
    os.system(f"mkdir -p {gfxdir_norm} {gfxdir_log}")

    for nADs in [6, 8, 7]:
        for site in [1, 2, 3]:
            for det in dets_for(site):
                if not det_active(nADs, site, det):
                    continue
                desc = f"{nADs}ad_eh{site}_ad{det}"
                c = plot_h_ncap(nADs, site, det, log=False)
                c.SaveAs(f"{gfxdir_norm}/ncap_norm_{desc}.png")
                c = plot_h_ncap(nADs, site, det, log=True)
                c.SaveAs(f"{gfxdir_log}/ncap_log_{desc}.png")


def overlay_h_ncap():
    R.gStyle.SetOptStat(0)

    colors = [R.kRed, R.kBlue, R.kMagenta, R.kGreen,
              R.kOrange, R.kBlack, R.kYellow, R.kPink]
    hists = [None] * 8

    for nADs in [6, 8, 7]:
        for site in [1, 2, 3]:
            for det in dets_for(site):
                if not det_active(nADs, site, det):
                    continue
                _h_ncap, _h_sing, h_ncap_sub = get_h_ncap(nADs, site, det)
                idt = idet(site, det)
                if hists[idt] is None:
                    hists[idt] = keep(h_ncap_sub.Clone(f"h_AD{det}"))
                    print(hists[idt])
                else:
                    hists[idt].Add(h_ncap_sub)

    for i, h in enumerate(hists):
        h.SetLineColor(colors[i])
        h.Scale(1/h.Integral())
        opt = " same" if i != 0 else ""
        h.Draw("hist" + opt)

    R.gPad.BuildLegend()
    R.gPad.SetLogy()
    R.gPad.SaveAs("gfx/overlay_h_ncap.png")



if __name__ == '__main__':
    R.gROOT.SetBatch(True)
    plot_h_ncap_all()
