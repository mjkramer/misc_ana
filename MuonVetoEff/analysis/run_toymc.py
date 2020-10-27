#!/usr/bin/env python3

import argparse
import os
import sys


def read_data_file(path):
    result = {}

    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, val, *_ = line.split()
        result[key] = val

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template_dir")
    ap.add_argument("cut_pe")
    ap.add_argument("time_s")
    args = ap.parse_args()

    fit_home = os.getenv("LBNL_FIT_HOME")

    if not fit_home:
        print("You forgot to set LBNL_FIT_HOME")
        sys.exit(1)

    outdir = f"fit_input/shVeto_{args.cut_pe}pe_{args.time_s}s"
    outdir = os.path.abspath(outdir)
    os.system(f"mkdir -p {outdir}")

    for nADs in [6, 8, 7]:
        theta13file = f"Theta13-inputs_P17B_inclusve_{nADs}ad.txt"
        template = f"{args.template_dir}/{theta13file}"
        outfile = f"{outdir}/{theta13file}"
        os.system(f"./genText4Veto.py {template} {outfile} {nADs} {args.cut_pe} {args.time_s}")
        os.system(f"cp {args.template_dir}/accidental_eprompt_shapes_{nADs}ad.root {outdir}")

    os.environ["LBNL_FIT_INDIR"] = outdir
    os.environ["LBNL_FIT_OUTDIR"] = outdir

    S = f"{fit_home}/scripts/run_chain.sh"
    os.system(f"{S} genToys & {S} genEvisEnu & {S} genSuperHists & {S} genPredIBD & wait; {S} genCovMat")

    data_file = read_data_file(f"{fit_home}/toySpectra/data_file/dyb_data_v1_nominal.txt")
    s2t13 = data_file["sinSq2Theta13"]
    dm2ee = data_file["deltaMSqee"]

    os.system(f"mv {outdir}/PredictedIBD.root {fit_home}/PredictedIBD_bak.root")
    cwd = os.getcwd()
    os.chdir(f"{fit_home}/toySpectra")
    os.system(f'root -b -q LoadClasses.C "genPredictedIBD.C+({s2t13}, {dm2ee})"')
    os.system(f"mv {outdir}/PredictedIBD.root {outdir}/PredictedIBD_osc.root")
    os.system(f"mv {outdir}/PredictedIBD_bak.root {outdir}/PredictedIBD.root")
    os.chdir(cwd)

    os.system(f"./genHists4Veto.py {outdir}")

    os.system(f"{S} shapeFit")


if __name__ == '__main__':
    main()
