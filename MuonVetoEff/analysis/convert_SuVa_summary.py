#!/usr/bin/env python3
"""Converts a summary CSV file from SuperVariator's format to the one used in
plot_fit_results"""

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile")
    args = ap.parse_args()

    print(",cut_pe,time_s,s2t_best,s2t_min1sigma,s2t_max1sigma,dm2_best,dm2_min1sigma,dm2_max1sigma")

    for line in open(args.infile).readlines()[1:]:
        parts = line.strip().split(",")
        titleparts = parts[1].split("_")
        cut_pe_str = "%.1f" % float(titleparts[1])
        time_s_str = titleparts[3]
        newparts = [parts[0], cut_pe_str, time_s_str, *parts[2:8]]
        print(",".join(newparts))


if __name__ == '__main__':
    main()
