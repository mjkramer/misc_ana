#!/usr/bin/env python3

import os


def days_for_phase(nADs):
    if nADs == 6:
        return range(0, 217 + 1)
    elif nADs == 8:
        return range(300, 1824 + 1)
    elif nADs == 7:
        return range(1860, 2076 + 1)
    raise


def inputs(hall, nADs):
    for day in days_for_phase(nADs):
        path = f"results/muons.dbd.eh{hall}.{day:04d}.root"
        if os.path.exists(path):
            yield path


def main():
    os.system("mkdir -p merged")
    for hall in [1, 2, 3]:
        for nADs in [6, 8, 7]:
            infiles = " ".join(inputs(hall, nADs))
            cmd = f"hadd merged/muons.pbp.eh{hall}.{nADs}ad.root {infiles}"
            os.system(cmd)


if __name__ == '__main__':
    main()
