#!/usr/bin/env python3

import argparse

import pandas as pd


def read_listfile(listfile):
    result = {}
    for line in open(listfile):
        parts = line.split(".")
        runno = int(parts[-6])
        fileno = int(parts[-2][1:])
        result[(runno, fileno)] = line.strip()
    return result


def read_runlist(dbd_runlist):
    return pd.read_csv(dbd_runlist, sep=r"\s+", header=None,
                       names=["day", "hall", "runno", "fileno"],
                       index_col=["day", "hall"]).sort_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listfile")
    ap.add_argument("dbd_runlist")
    ap.add_argument("day", type=int)
    ap.add_argument("hall", type=int)
    args = ap.parse_args()

    pathdict = read_listfile(args.listfile)
    runlist = read_runlist(args.dbd_runlist)

    for _idx, runno, fileno in runlist.loc[(args.day, args.hall)].itertuples():
        print(pathdict[(runno, fileno)])


if __name__ == '__main__':
    main()
