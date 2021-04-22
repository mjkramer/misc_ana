#!/usr/bin/env python3

import argparse
from random import gauss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--num", type=int, default=100,
                    help="Number of throws")

    cuts = []

    def add_cut(name, mean, sigma):
        ap.add_argument(f"--{name}-mean", default=mean)
        ap.add_argument(f"--{name}-sigma", default=sigma)
        cuts.append(name.replace("-", "_"))

    add_cut("shower-pe", 3e5, 1e5)
    add_cut("shower-sec", 1, 0.3)
    add_cut("delayed-emin-mev", 6, 0.5)
    add_cut("prompt-emin-mev", 0.7, 0.1)

    args = ap.parse_args()

    def gen(name):
        mean = getattr(args, f"{name}_mean")
        sigma = getattr(args, f"{name}_sigma")
        return gauss(mean, sigma)

    for i in range(args.num):
        title = f"Cut{i}"
        cut_str = ",".join([f"{cut}={gen(cut)}"
                            for cut in cuts])
        print(f"{title} {cut_str}")


if __name__ == '__main__':
    main()
