#!/usr/bin/env python3
"Dump list of input stage1 files for a given DAY"

import argparse
import os

import pandas as pd


TAG = "p20a"
# LISTFILE = "/global/project/projectdirs/dayabay/data/dropbox/p20a_recon/paths.physics.good.p20a.v1.sync.txt"
DBD_RUNLIST = "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/merge1_input/p20a/dbd_runlist_p20a.txt"


def stage1_fbf_path(hall, runno, fileno, tag):
    home = os.environ["IBDSEL_HOME"]
    subrun = runno // 100 * 100
    path = f"{home}/../data/stage1_fbf/{tag}/EH{hall}/{subrun:07d}/{runno:07d}/stage1.fbf.eh{hall}.{runno:07d}.{fileno:04d}.root"
    path = os.path.normpath(path)
    assert os.path.exists(path)
    return path


class DaySplitter:
    def __init__(self):
        # self.paths = self._read_listfile()
        self.runlist = self._read_runlist()

    def dump(self, day, hall, tag=TAG):
        for _idx, runno, fileno in self.runlist.loc[(day, hall)].itertuples():
            # path = self.paths[(runno, fileno)]
            path = stage1_fbf_path(hall, runno, fileno, tag)
            print(path)

    # @staticmethod
    # def _read_listfile(listfile=LISTFILE):
    #     result = {}
    #     for line in open(listfile):
    #         parts = line.split(".")
    #         runno = int(parts[-6])
    #         fileno = int(parts[-2][1:])
    #         result[(runno, fileno)] = line.strip()
    #     return result

    @staticmethod
    def _read_runlist(dbd_runlist=DBD_RUNLIST):
        return pd.read_csv(dbd_runlist, sep=r"\s+", header=None,
                           names=["day", "hall", "runno", "fileno"],
                           index_col=["day", "hall"]).sort_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("day", type=int)
    ap.add_argument("hall", type=int)
    args = ap.parse_args()

    ds = DaySplitter()
    ds.dump(args.day, args.hall)


if __name__ == '__main__':
    main()
