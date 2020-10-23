#!/usr/bin/env python3

import os
import sys


def main():
    hall = int(sys.argv[1])
    startday = int(sys.argv[2])  # inclusive
    endday = int(sys.argv[3])   # exclusive

    for day in range(startday, endday):
        path = f"/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/stage1_dbd/2020_01_26/EH{hall}/stage1.dbd.eh{hall}.{day:04d}.root"
        if os.path.exists(path):
            cmd = f"_build/condenser.exe {path} results/muons.dbd.eh{hall}.{day:04d}.root"
            print(cmd)
            os.system(cmd)


if __name__ == '__main__':
    main()
