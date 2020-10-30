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


def run_toymc(template_dir, dirname, no_fit=False, cut_pe=None, time_s=None,
              s2t13=None, dm2=None, bcw_bins=False):
    C = os.system

    fit_home = os.getenv("LBNL_FIT_HOME")
    if not fit_home:
        print("You forgot to set LBNL_FIT_HOME")
        sys.exit(1)

    outdir = os.path.abspath(f"fit_results/{dirname}")
    C(f"mkdir -p {outdir}")
    os.environ["LBNL_FIT_INDIR"] = outdir
    os.environ["LBNL_FIT_OUTDIR"] = outdir

    for nADs in [6, 8, 7]:
        theta13file = f"Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        template = f"{template_dir}/{theta13file}"
        outfile = f"{outdir}/{theta13file}"
        if cut_pe and time_s:
            C(f"./genText4Veto.py {template} {outfile} {nADs} {cut_pe} {time_s}")
        else:
            C(f"cp {template} {outfile}")
        C(f"cp {template_dir}/accidental_eprompt_shapes_{nADs}ad.root {outdir}")

    confdir = f"{outdir}/data_file"
    C(f"mkdir -p {confdir}")
    os.environ["LBNL_TOY_CONFIG_DIR"] = confdir
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

    if bcw_bins:
        os.environ["LBNL_FIT_BINNING"] = "BCW"

    S = f"{fit_home}/scripts/run_chain.sh"
    C(f"{S} genToys & {S} genEvisEnu & {S} genSuperHists & {S} genPredIBD & wait; {S} genCovMat")

    C(f"./genHists4Veto.py {outdir}")

    if not no_fit:
        C(f"{S} shapeFit")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template_dir")
    ap.add_argument("outdirname")
    ap.add_argument("--no-fit", action="store_true")
    ap.add_argument("--cut-pe", type=float)
    ap.add_argument("--time-s", type=float)
    ap.add_argument("--s2t13", type=float)
    ap.add_argument("--dm2", type=float)
    ap.add_argument("--bcw-bins", action="store_true")
    args = ap.parse_args()

    run_toymc(args.template_dir,
              args.outdirname,
              no_fit=args.no_fit,
              cut_pe=args.cut_pe,
              time_s=args.time_s,
              s2t13=args.s2t13,
              dm2=args.dm2,
              bcw_bins=args.bcw_bins)


if __name__ == '__main__':
    main()
