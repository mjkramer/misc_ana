#!/usr/bin/env python3

from glob import glob
import os
import sys

import ROOT as R

from muVetoEff import vetoEff


def get_vetoEff(f, det):
    if f.Get(f"h_adMuons_ad{det}"):
        return vetoEff(f, det, 3e5, 0.4004)
    else:
        return 0.0


def main():
    hall = int(sys.argv[1])
    with open(f"output/vetoEff_dbd_eh{hall}.txt", "w") as outf:
        outf.write("day effAD1 effAD2 effAD3 effAD4\n")
        expr = f"../condenser/results/muons.dbd.eh{hall}.*.root"
        for fname in sorted(glob(expr)):
            day = int(os.path.basename(fname).split(".")[3])
            f = R.TFile(fname)
            vals = [str(get_vetoEff(f, det)) for det in [1, 2, 3, 4]]
            outf.write(f"{day} {' '.join(vals)}\n")


if __name__ == '__main__':
    main()
