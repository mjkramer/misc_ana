#!/usr/bin/env python3

import argparse

import ROOT as R

SRCFILE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/Fitter" + \
    "/fn_spectrum/P15A_fn_spectrum.root"


def fastn_func():
    fFastN = R.TF1("fFastN", "[0]*(1 - [1]*exp(-x/[2]))", 0, 100)
    fFastN.SetParLimits(0, 0, 0.1)
    fFastN.SetParLimits(1, 0, 1)
    fFastN.SetParLimits(2, 0, 1000)
    fFastN.SetParameter(0, 0.005)
    fFastN.SetParameter(1, 0.001)
    fFastN.SetParameter(2, 10)
    return fFastN


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outfile")
    args = ap.parse_args()

    func = fastn_func()
    src = R.TFile(SRCFILE)
    out = R.TFile(args.outfile, "RECREATE")

    for hall in [1, 2, 3]:
        for det in [1, 2, 3, 4] if hall == 3 else [1, 2]:
            idet = (hall - 1) * 2 + det

            src_hist = src.Get(f"h_{idet}AD_fn_fine")

            out_hname = f"h_fastn_eh{hall}_ad{det}"
            out_htitle = f"Fast neutron spectrum, EH{hall}-AD{det}"
            out_hist = R.TH1F(out_hname, out_htitle, 400, 0, 20)

            src_hist.Fit(func, "0", "goff")

            for ibin in range(1, out_hist.GetNbinsX() + 1):
                if out_hist.GetBinLowEdge(ibin + 1) <= 0.7:
                    continue
                if out_hist.GetBinLowEdge(ibin) >= 17:
                    break
                x = out_hist.GetBinCenter(ibin)
                y = func.Eval(x)
                out_hist.SetBinContent(ibin, y)

            out_hist.Scale(1/out_hist.Integral(), "nosw2")

            out.cd()
            out_hist.Write()


if __name__ == '__main__':
    main()
