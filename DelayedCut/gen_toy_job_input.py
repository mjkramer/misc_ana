#!/usr/bin/env python3

import argparse
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cut_list_file")
    ap.add_argument("template_dir")
    args = ap.parse_args()

    for line in open(args.cut_list_file):
        mev = line.strip()
        print(f"{os.path.abspath(args.template_dir)} {mev}")


if __name__ == '__main__':
    main()
