#!/usr/bin/env python3

# testing

from root_pandas import read_root
from glob import glob
import os

def parse_path(path):
    fname = path.split("/")[-1]
    middle = ".".join(fname.split(".")[1:-1])
    parts = middle.split("_")
    usec_before, usec_after, emin_after = int(parts[0]), int(parts[1]), float(parts[2])
    return usec_before, usec_after, emin_after

def read_acc_rate(path):
    tree = read_root(path, "results", ["detector", "accDaily"])
    for idx, row in tree.iterrows():
        yield row.detector, row.accDaily

def main():
    print("usec_before usec_after emin_after det acc_day")
    for path in glob("stage2_files/stage2.*.root"):
        usec_before, usec_after, emin_after = parse_path(path)
        for det, acc_day in read_acc_rate(path):
            print(f"{usec_before} {usec_after} {emin_after} {det} {acc_day:.4f}")

if __name__ == '__main__':
    main()
