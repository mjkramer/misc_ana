#!/usr/bin/env python3

import argparse

import numpy as np
import ROOT as R

from genText4Veto import dets_for, idet

nbins_lbnl = 37
nbins_fine = 240


def binning_lbnl():
    edges = np.concatenate([[0.7],
                            np.arange(1, 8, 0.2),
                            [8, 12]])
    assert len(edges) == 1 + nbins_lbnl
    return edges


def binning_fine():
    return np.linspace(0, 12, 1 + nbins_fine)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    args = ap.parse_args()

    infile = R.TFile(f"{args.outdir}/PredictedIBD_osc.root")

    for stage in [1, 2, 3]:
        nADs = [6, 8, 7][stage-1]
        outfile = R.TFile(f"{args.outdir}/ibd_eprompt_shapes_{nADs}ad.root",
                          "RECREATE")

        for site in [1, 2, 3]:
            for det in dets_for(site):
                i = idet(site, det)
                h_in = infile.Get(f"h_nominal_stage{stage}_ad{i+1}")

                name_lbnl = f"h_ibd_eprompt_inclusive_eh{site}_ad{det}"
                name_fine = f"h_ibd_eprompt_fine_inclusive_eh{site}_ad{det}"

                h_lbnl = h_in.Rebin(nbins_lbnl, name_lbnl, binning_lbnl())
                h_fine = h_in.Rebin(nbins_fine, name_fine, binning_fine())

                outfile.cd()
                h_lbnl.Write()
                h_fine.Write()

        outfile.Close()


if __name__ == '__main__':
    main()
