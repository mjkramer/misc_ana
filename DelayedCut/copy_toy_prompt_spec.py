#!/usr/bin/env python3

import argparse

import ROOT as R

from gen_text_for_toy import dets_for, idet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    args = ap.parse_args()

    # bgsys also works since we're just taking the nominal spectra
    infile = R.TFile(f"{args.outdir}/toys/toySpectra_sigsys.root")

    for stage in [1, 2, 3]:
        nADs = [6, 8, 7][stage-1]
        outfile = R.TFile(f"{args.outdir}/ibd_eprompt_shapes_{nADs}ad.root",
                          "RECREATE")

        for site in [1, 2, 3]:
            for det in dets_for(site):
                i = idet(site, det)
                h_in = infile.Get(f"h_nominal_stage{stage}_ad{i+1}")
                outfile.cd()
                h_in.Write(f"h_ibd_eprompt_inclusive_eh{site}_ad{det}")

        outfile.Close()


if __name__ == '__main__':
    main()
