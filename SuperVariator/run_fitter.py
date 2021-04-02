#!/usr/bin/env python3

import argparse
import os
import sys

from common import CutSpec


def run_fitter(template_dir, outdir_name, cuts: str,
               period=-1, bcw_bins=False):
    cuts = CutSpec.from_str(cuts)
    C = os.system

    fit_home = os.getenv("LBNL_FIT_HOME")
    if not fit_home:
        print("You forgot to set LBNL_FIT_HOME")
        sys.exit(1)
    S = f"{fit_home}/scripts/run_chain.sh"

    outdir = os.path.abspath(f"data/fit_results/{outdir_name}")
    os.environ["LBNL_FIT_INDIR"] = outdir
    os.environ["LBNL_FIT_OUTDIR"] = outdir
    if bcw_bins:
        os.environ["LBNL_FIT_BINNING"] = "BCW"
    os.environ["LBNL_FIT_EMIN"] = f"{cuts.prompt_emin_mev:.3f}"

    C(f"mkdir -p {outdir}")

    for nADs in [6, 8, 7]:
        theta13file = f"Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        # The * ensures we also copy the aux_ files if they exist
        C(f"cp {template_dir}/*{theta13file} {outdir}")
        C(f"cp {template_dir}/accidental_eprompt_shapes_{nADs}ad.root {outdir}")

    C(f"{S} genToys & {S} genEvisEnu & {S} genSuperHists & {S} genPredIBD & wait; {S} genCovMat")

    for nADs in [6, 8, 7]:
        C(f"cp {template_dir}/ibd_eprompt_shapes_{nADs}ad.root {outdir}")

    C(f"{S} shapeFit {period}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template_dir")
    ap.add_argument("outdir_name")
    ap.add_argument("--cuts")
    ap.add_argument("--period", type=int, default=-1)
    ap.add_argument("--bcw-bins", action="store_true")
    args = ap.parse_args()

    run_fitter(**vars(args))


if __name__ == '__main__':
    main()
