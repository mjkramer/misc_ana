from glob import glob
import os

import pandas as pd

from runAccUncMC import loadAccUncMC


def dump_accunc_vs_delcut(tag="delcut_firstPlusFine",
                          selnames=["delcut_first", "delcut_fine4to5"],
                          stage1name="2020_01_26"):
    outdir = f"summaries/accunc_vs_delcut/{tag}"
    os.system(f"mkdir -p {outdir}")

    results_prd = {}

    for nADs in [6, 8, 7]:
        results_prd[nADs] = []

        home = os.getenv("IBDSEL_HOME")
        stage2_home = f"{home}/../data/stage2_pbp"

        for selname in selnames:
            direcs = glob(f"{stage2_home}/{stage1name}@{selname}_*")
            for direc in direcs:
                cutname = direc.split("_")[-1]
                print(nADs, selname, cutname)
                cut_mev = float(cutname[:-3])
