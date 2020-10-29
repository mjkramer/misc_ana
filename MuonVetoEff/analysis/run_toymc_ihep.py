#!/usr/bin/env python3

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


def get_outdir(dirname):
    "Assumes we are in MuonVetoEff/analysis"
    return os.path.abspath(f"fit_results/{dirname}")


def shapefit(dirname):
    fit_home = os.getenv("LBNL_FIT_HOME")
    os.system(f"{fit_home}/scripts/run_chain.sh shapeFit")


def check_fit_home():
    fit_home = os.getenv("LBNL_FIT_HOME")

    if not fit_home:
        print("You forgot to set LBNL_FIT_HOME")
        sys.exit(1)

    return fit_home


def run_toymc_ihep(do_fit=True, dirname="ihep_official"):
    fit_home = check_fit_home()

    template_dir = f"{fit_home}/example/IHEP-official"

    outdir = get_outdir(dirname)
    os.system(f"mkdir -p {outdir}")

    for nADs in [6, 8, 7]:
        theta13file = f"Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        template = f"{template_dir}/{theta13file}"
        outfile = f"{outdir}/{theta13file}"
        os.system(f"cp {template} {outfile}")
        os.system(f"cp {template_dir}/accidental_eprompt_shapes_{nADs}ad.root {outdir}")

    os.environ["LBNL_FIT_INDIR"] = outdir
    os.environ["LBNL_FIT_OUTDIR"] = outdir
    os.environ["LBNL_FIT_BINNING"] = "BCW"

    S = f"{fit_home}/scripts/run_chain.sh"
    os.system(f"{S} genToys & {S} genEvisEnu & {S} genSuperHists & {S} genPredIBD & wait; {S} genCovMat")

    data_file = read_data_file(f"{fit_home}/toySpectra/data_file/dyb_data_v1_nominal.txt")
    s2t13 = data_file["sinSq2Theta13"]
    dm2ee = data_file["deltaMSqee"]

    os.system(f"mv {outdir}/PredictedIBD.root {outdir}/PredictedIBD_bak.root")
    cwd = os.getcwd()
    os.chdir(f"{fit_home}/toySpectra")
    os.system(f'root -b -q LoadClasses.C "genPredictedIBD.C+({s2t13}, {dm2ee})"')
    os.system(f"mv {outdir}/PredictedIBD.root {outdir}/PredictedIBD_osc.root")
    os.system(f"mv {outdir}/PredictedIBD_bak.root {outdir}/PredictedIBD.root")
    os.chdir(cwd)

    os.system(f"./genHists4Veto_ihep.py {outdir}")

    if do_fit:
        shapefit(dirname)


def main():
    run_toymc_ihep()


if __name__ == '__main__':
    main()
