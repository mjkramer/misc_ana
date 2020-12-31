#!/usr/bin/env python3

import argparse
import os
import sys


def read_data_file(path):       # toy MC datafile
    result = {}

    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, val, *_ = line.split()
        result[key] = val

    return result


def dump_data_file(path, data):
    with open(path, 'w') as fout:
        for key, val in data.items():
            fout.write(f"{key} {val}\n")


def run_fitter(template_dir, dirname, no_fit=False, cut_mev=None,
               s2t13=None, dm2=None, bcw_bins=False, use_data=False, period=-1,
               copy_from=None):
    C = os.system

    fit_home = os.getenv("LBNL_FIT_HOME")
    if not fit_home:
        print("You forgot to set LBNL_FIT_HOME")
        sys.exit(1)
    S = f"{fit_home}/scripts/run_chain.sh"

    outdir = os.path.abspath(f"fit_results/{dirname}")
    confdir = f"{outdir}/data_file"
    os.environ["LBNL_FIT_INDIR"] = outdir
    os.environ["LBNL_FIT_OUTDIR"] = outdir
    os.environ["LBNL_TOY_CONFIG_DIR"] = confdir
    if bcw_bins:
        os.environ["LBNL_FIT_BINNING"] = "BCW"

    C(f"mkdir -p {outdir}")
    if copy_from:
        C(f"cp -R {copy_from}/{os.path.basename(dirname)}/* {outdir}")
    else:
        for nADs in [6, 8, 7]:
            theta13file = f"Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
            template = f"{template_dir}/{theta13file}"
            outfile = f"{outdir}/{theta13file}"
            if (not use_data) and cut_mev:
                C(f"./gen_text_for_toy.py {template} {outfile} {nADs} {cut_mev}")
            else:
                C(f"cp {template} {outfile}")
            C(f"cp {template_dir}/accidental_eprompt_shapes_{nADs}ad.root {outdir}")

        C(f"mkdir -p {confdir}")
        for config in ["nominal", "nominal_fine", "sigsys", "bgsys"]:
            data_file = f"dyb_data_v1_{config}.txt"
            orig_data_file = f"{fit_home}/toySpectra/data_file/{data_file}"
            if s2t13 is not None and dm2 is not None:
                data = read_data_file(orig_data_file)
                data["sinSq2Theta13"] = s2t13
                data["deltaMSqee"] = dm2
                dump_data_file(f"{confdir}/{data_file}", data)
            else:
                C(f"cp {orig_data_file} {confdir}/{data_file}")

        C(f"{S} genToys & {S} genEvisEnu & {S} genSuperHists & {S} genPredIBD & wait; {S} genCovMat")

        if use_data:
            for nADs in [6, 8, 7]:
                C(f"cp {template_dir}/ibd_eprompt_shapes_{nADs}ad.root {outdir}")
        else:
            C(f"./copy_toy_prompt_spec.py {outdir}")

    if not no_fit:
        C(f"{S} shapeFit {period}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template_dir")
    ap.add_argument("dirname")
    ap.add_argument("--no-fit", action="store_true")
    ap.add_argument("--cut-mev", type=float)
    ap.add_argument("--s2t13", type=float)
    ap.add_argument("--dm2", type=float)
    ap.add_argument("--bcw-bins", action="store_true")
    ap.add_argument("--use-data", action="store_true")
    ap.add_argument("--period", type=int, default=-1)
    ap.add_argument("--copy-from")
    args = ap.parse_args()

    run_fitter(**vars(args))


if __name__ == '__main__':
    main()
