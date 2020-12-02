#!/usr/bin/env python3

import argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cut_list_file")
    ap.add_argument("template_dir")
    args = ap.parse_args()

    for line in open(args.cut_list_file):
        pe, sec = line.strip().split()
        print(f"{args.template_dir} {pe} {sec}")


if __name__ == '__main__':
    main()
