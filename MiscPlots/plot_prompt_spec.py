import os

import ROOT as R

from util import dets_for, keep


STAGE2_PBP_BASE = "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/stage2_pbp"

R.gStyle.SetOptStat(0)


def plot_prompt_spec(tag="2021_02_03", config="delcut_fourth_6.000MeV"):
    gfxdir = f"gfx/prompt_spec/{tag}@{config}"
    os.system(f"mkdir -p {gfxdir}")

    c = keep(R.TCanvas("c_prompt", "c_prompt", 2100, 500))
    c.Divide(3, 1)

    for hall in [1, 2, 3]:
        hname = f"h_prompt_eh{hall}"
        htitle = f"Raw prompt spectrum, EH{hall}"
        h = keep(R.TH1F(hname, htitle, 240, 0, 12))
        h.SetXTitle("MeV")

        for nADs in [6, 8, 7]:
            path = f"{STAGE2_PBP_BASE}/{tag}@{config}/stage2.pbp.eh{hall}.{nADs}ad.root"
            f = R.TFile(path)
            h.SetDirectory(f)
            for det in dets_for(hall, nADs):
                tree = f.Get(f"ibd_AD{det}")
                tree.Draw(f"eP>>+{hname}", "", "goff")
            keep(h)

        c.cd(hall)
        h.Draw()
        R.gPad.Modified()
        R.gPad.Update()

    c.SaveAs(f"{gfxdir}/prompt_spec_3halls.pdf")
    c.SaveAs(f"{gfxdir}/prompt_spec_3halls.png")
