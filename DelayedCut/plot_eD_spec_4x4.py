#!/usr/bin/env python3

import os

import ROOT as R

from util import keep

R.gROOT.SetBatch(True)


def draw_4x4(tfile, nADs, listADs, tag):
    cname = f"c_{nADs}ad_{tag}"
    c = keep(R.TCanvas(cname, cname, 1400, 1000))
    c.Divide(2, 2)

    for ipad, (hall, ad) in enumerate(listADs):
        c.cd(ipad+1)
        h = keep(tfile.Get(f"h_ncap_{nADs}ad_eh{hall}_ad{ad}"))
        if not h:
            continue
        h.Draw("HIST")
        # R.gPad.SetLogy()

    return c


def main():
    os.system("mkdir -p gfx/eD_spec_4x4")

    home = os.getenv("IBDSEL_HOME")
    fname = f"{home}/static/ncap_spec/ncap_spec_P17B.root"
    f = R.TFile(fname)

    for nADs in [6, 8, 7]:
        near = [(1, 1), (1, 2), (2, 1), (2, 2)]
        far = [(3, 1), (3, 2), (3, 3), (3, 4)]

        c = draw_4x4(f, nADs, near, "near")
        c.SaveAs(f"gfx/eD_spec_4x4/eD_{nADs}ad_near.png")

        c = draw_4x4(f, nADs, far, "far")
        c.SaveAs(f"gfx/eD_spec_4x4/eD_{nADs}ad_far.png")


if __name__ == '__main__':
    main()
