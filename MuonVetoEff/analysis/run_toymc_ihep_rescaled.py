#!/usr/bin/env python3

import os

import numpy as np
import ROOT as R

from run_toymc_ihep import run_toymc_ihep, get_outdir, shapefit
from run_toymc_ihep import check_fit_home
from genText4Veto import dets_for, idet
from util import read_theta13_file


def rescale_hists(dirname):
    outdir = get_outdir(dirname)

    for stage in [1, 2, 3]:
        nADs = [6, 8, 7][stage-1]

        fname = f"{outdir}/ibd_eprompt_shapes_{nADs}ad.root"
        fname_orig = fname[:-5] + "_orig.root"
        os.system(f"mv {fname} {fname_orig}")
        f = R.TFile(fname, "RECREATE")
        f_orig = R.TFile(fname_orig)

        theta13file = f"{outdir}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        data = read_theta13_file(theta13file)
        nIBDs = data[1]

        for site in [1, 2, 3]:
            for det in dets_for(site):
                i = idet(site, det)
                h = f_orig.Get(f"h_ibd_eprompt_inclusive_eh{site}_ad{det}")
                h_fine = f_orig.Get(f"h_ibd_eprompt_fine_inclusive_eh{site}_ad{det}")

                print(h.GetName(), h.Integral())
                print(h_fine.GetName(), h_fine.Integral())

                assert np.isclose(h.Integral(), h_fine.Integral())

                factor = nIBDs[i] / h.Integral() if h.Integral() else 1
                h.Scale(factor)
                h_fine.Scale(factor)

                assert np.isclose(h.Integral(), nIBDs[i])
                assert np.isclose(h_fine.Integral(), nIBDs[i])

                f.cd()
                h.Write()
                h_fine.Write()


def run_toymc_ihep_rescaled(dirname, copy_from):
    check_fit_home()

    outdir = get_outdir(dirname)

    os.environ["LBNL_FIT_INDIR"] = outdir
    os.environ["LBNL_FIT_OUTDIR"] = outdir
    os.environ["LBNL_FIT_BINNING"] = "BCW"

    if copy_from:
        os.system(f"cp -r {get_outdir(copy_from)} {outdir}")
    else:
        run_toymc_ihep(dirname=dirname, do_fit=False)

    rescale_hists(dirname)

    shapefit(dirname)


def main():
    run_toymc_ihep_rescaled(dirname='ihep_official_rescaled',
                            copy_from='ihep_official')


if __name__ == '__main__':
    main()
