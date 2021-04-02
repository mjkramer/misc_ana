#!/usr/bin/env python3

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cutlist")
    ap.add_argument("input_base")
    args = ap.parse_args()

    for line in open(args.cutlist):
        title, cut_str = line.strip().split()
        direc = f"{args.input_base}_{title}"
        print(f"{direc} {title} {cut_str}")


if __name__ == '__main__':
    main()
