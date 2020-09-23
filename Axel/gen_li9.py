#!/usr/bin/env python3

import argparse

import ROOT as R

SRCFILE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/Fitter" + \
    "/li9_spectrum/8he9li_nominal_spectrum_P15A.root"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outfile")
    args = ap.parse_args()

    src = R.TFile(SRCFILE)
    out = R.TFile(args.outfile, "RECREATE")

    src_hist = src.Get("h_nominal")

    out_hname = "h_li9"
    out_htitle = "Li9/He8 spectrum"
    out_hist = R.TH1F(out_hname, out_htitle, 400, 0, 20)

    for ibin in range(1, 240 + 1):
        out_hist.SetBinContent(ibin, src_hist.GetBinContent(ibin))

    out_hist.Scale(1/out_hist.Integral(), "nosw2")

    out.cd()
    out_hist.Write()


if __name__ == '__main__':
    main()
