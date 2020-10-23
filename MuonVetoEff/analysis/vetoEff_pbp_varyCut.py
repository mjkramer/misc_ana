#!/usr/bin/env python3

import sys

import numpy as np
import ROOT as R

from muVetoEff import vetoEff


CUTS = np.arange(1.8e5, 5.001e5, 0.1e5)
TIMES = np.arange(0.1, 2.01, 0.1)


def get_vetoEff(f, det, cut, time):
    if f.Get(f"h_adMuons_ad{det}"):
        return vetoEff(f, det, cut, time)
    else:
        return 0.0


def main():
    hall = int(sys.argv[1])
    nADs = int(sys.argv[2])

    with open(f"output/vetoEff_pbp_eh{hall}_{nADs}ad.txt", "w") as outf:
        outf.write("cut_pe time_s effAD1 effAD2 effAD3 effAD4\n")
        f = R.TFile(f"../condenser/merged/muons.pbp.eh{hall}.{nADs}ad.root")
        for cut in CUTS:
            for time in TIMES:
                vals = [str(get_vetoEff(f, det, cut, time))
                        for det in [1, 2, 3, 4]]
                outf.write(f"{cut} {time} {' '.join(vals)}\n")


if __name__ == '__main__':
    main()
