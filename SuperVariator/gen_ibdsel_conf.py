#!/usr/bin/env python3

import argparse
import os

# From IbdSel:
from config_file import ConfigFile, template_path

from common import CutSpec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cutlist")
    ap.add_argument("--outdir", default=os.environ["IBDSEL_CONFIGDIR"])
    ap.add_argument("-t", "--template", default=template_path())
    args = ap.parse_args()

    os.system(f"mkdir -p {args.outdir}")

    config = ConfigFile(args.template)

    for line in open(args.cutlist):
        title, cut_str = line.strip().split()
        cut = CutSpec.from_str(cut_str)
        config["ibdShowerMuChgCut"] = cut.shower_pe
        config["ibdShowerMuPostVeto_us"] = 1e6 * cut.shower_sec
        config["ibdDelayedEmin"] = cut.delayed_emin_mev
        config["ibdDmcEminAfter"] = cut.delayed_emin_mev
        config["ibdPromptEmin"] = cut.prompt_emin_mev
        config["ibdDmcEminBefore"] = cut.prompt_emin_mev
        study = os.path.basename(args.outdir)
        outfile = f"config.{study}_{title}.txt"
        config.write(f"{args.outdir}/{outfile}")


if __name__ == '__main__':
    main()

