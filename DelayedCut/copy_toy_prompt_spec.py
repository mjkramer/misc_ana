#!/usr/bin/env python3

import argparse

import ROOT as R

from gen_text_for_toy import dets_for, idet
from util import read_theta13_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('outdir')
    args = ap.parse_args()

    # bgsys also works since we're just taking the nominal spectra
    infile = R.TFile(f"{args.outdir}/toys/toySpectra_sigsys.root")

    for stage in [1, 2, 3]:
        nADs = [6, 8, 7][stage - 1]
        outfile = R.TFile(f"{args.outdir}/ibd_eprompt_shapes_{nADs}ad.root",
                          "RECREATE")
        t13file = f"{args.outdir}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        del_effs = read_theta13_file(t13file)["delcut_eff"]

        for site in [1, 2, 3]:
            for det in dets_for(site):
                i = idet(site, det)
                h_in = infile.Get(f"h_nominal_stage{stage}_ad{i+1}")
                h_in.Scale(del_effs[i])
                outfile.cd()
                h_in.Write(f"h_ibd_eprompt_inclusive_eh{site}_ad{det}")

        outfile.Close()


if __name__ == '__main__':
    main()
