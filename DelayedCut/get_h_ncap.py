#!/usr/bin/env python3

import os
import sys

import ROOT as R

sys.path += [os.path.dirname(__file__) + "/../MuonVetoEff/analysis"]
from util import read_theta13_file, T13_ROWS


STAGE2_FILE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/data" + \
    "/stage2_pbp/2020_01_26@del4MeV/stage2.pbp.eh1.8ad.root"

THETA13_FILE = "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data" + \
    "/fit_input/2020_01_26@del4MeV/Theta13-inputs_P17B_inclusive_8ad.txt"


def get_h_ncap(stage2_file=STAGE2_FILE, theta13_file=THETA13_FILE, det=1):
    f = R.TFile(stage2_file)
    R.gROOT.cd()
    h_ncap = R.TH1F("h_ncap", "Neutron capture spectrum", 160, 4, 12)
    tree = f.Get(f"ibd_AD{det}")
    tree.Draw("eD>>h_ncap", "", "goff")

    h_sing_orig = f.Get(f"h_single_AD{det}")
    h_sing = h_ncap.Clone("h_sing")
    h_sing.SetTitle("Singles")
    h_sing.Reset()

    for xbin in range(h_sing_orig.FindBin(4), h_sing_orig.FindBin(12)+1):
        h_sing.Fill(h_sing_orig.GetBinCenter(xbin),
                    h_sing_orig.GetBinContent(xbin))

    h_sing.Scale(1/h_sing.Integral())

    t13f = read_theta13_file(theta13_file)

    # XXX need to convert [1,4] det into [1,8] det
    # until then we only support EH1

    eff_mu = t13f[T13_ROWS["veto_eff"]][det-1]
    eff_dmc = t13f[T13_ROWS["mult_eff"]][det-1]
    livetime = t13f[T13_ROWS["livetime"]][det-1]
    acc_daily = t13f[T13_ROWS["acc_bkg"]][det-1]
    # li9_daily = t13f[T13_ROWS["li9_bkg"]][det-1]
    # fastn_daily = t13f[T13_ROWS["fastn_bkg"]][det-1]
    # alphan_daily = t13f[T13_ROWS["alphan_bkg"]][det-1]

    h_ncap_sub = h_ncap.Clone("h_ncap_sub")
    h_ncap_sub.SetTitle(h_ncap.GetTitle() + " (bkg sub)")

    total_acc = acc_daily * livetime * eff_mu * eff_dmc
    h_sing.Scale(total_acc)
    h_ncap_sub.Add(h_sing, -1)

    return h_ncap_sub, h_ncap, h_sing
