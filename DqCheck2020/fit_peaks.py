#!/usr/bin/env python3.7

import argparse
from collections import defaultdict
from glob import glob
import os

import ROOT as R

from util import keep


DEFAULT_STAGE2_DIR = "/global/homes/m/mkramer/mywork/ThesisAnalysis" + \
    "/IbdSel/data/stage2_dbd/p20a@nominal"


def singles_fit(h, emin, emax):
    res_ = h.Fit("gaus", "0SQ", "goff", emin, emax)
    res = res_.Get()
    return res.GetParams()[1], res.GetErrors()[1]


class PeakFitter:
    def __init__(self, stage2_dbd_dir=DEFAULT_STAGE2_DIR):
        self.tagconfig = os.path.basename(stage2_dbd_dir)

        # hall => day => det => h_singles
        self.hists = defaultdict(lambda: defaultdict(lambda: {}))

        for hall in [1, 2, 3]:
            for fname in glob(f"{stage2_dbd_dir}/EH{hall}/stage2.dbd.*.root"):
                day = int(fname.split(".")[-2])
                f = R.TFile(fname)
                for det in [1, 2, 3, 4]:
                    h = f.Get(f"h_single_AD{det}")
                    if h:
                        self.hists[hall][day][det] = keep(h)

    def dump_fit(self, name, emin, emax):
        fitdir = f"data/fits.{self.tagconfig}"
        os.system(f"mkdir -p {fitdir}")
        for hall in [1, 2, 3]:
            with open(f"{fitdir}/{name}.eh{hall}.csv", "w") as outf:
                with open(f"{fitdir}/{name}_err.eh{hall}.csv", "w") as outf_err:
                    for day in sorted(self.hists[hall]):
                        vals, vals_err = [], []
                        dets = [1, 2, 3, 4] if hall == 3 else [1, 2]
                        for det in dets:
                            try:
                                h = self.hists[hall][day][det]
                                peak, err = singles_fit(h, emin, emax)
                                vals.append(peak)
                                vals_err.append(err)
                            except KeyError:
                                vals.append(0)
                                vals_err.append(0)
                        valstr = " ".join(map(str, vals))
                        valstr_err = " ".join(map(str, vals_err))
                        outf.write(f"{day} {valstr}\n")
                        outf_err.write(f"{day} {valstr_err}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage2_dir")
    args = ap.parse_args()

    pf = PeakFitter(stage2_dbd_dir=args.stage2_dir)
    pf.dump_fit("k40", 1.4, 1.5)
    pf.dump_fit("tl208", 2.6, 2.8)


if __name__ == '__main__':
    main()
