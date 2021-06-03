#!/usr/bin/env python3

import argparse
from random import gauss


def limgauss(mean, sigma, xmin, xmax):
    while True:
        x = gauss(mean, sigma)
        if xmin <= x <= xmax:
            return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--num", type=int, default=100,
                    help="Number of throws")

    cuts = []

    def add_cut(name, mean, sigma, xmin, xmax):
        ap.add_argument(f"--{name}-mean", default=mean)
        ap.add_argument(f"--{name}-sigma", default=sigma)
        ap.add_argument(f"--{name}-min", default=xmin)
        ap.add_argument(f"--{name}-max", default=xmax)
        cuts.append(name.replace("-", "_"))

    add_cut("shower-pe", 3.4e5, 0.6e5, 2.2e5, 4.6e5)
    add_cut("shower-sec", 1.125, 0.4375, 0.25, 2)
    add_cut("delayed-emin-mev", 6, 0.5, 5, 7)
    add_cut("prompt-emin-mev", 0.75, 0.125, 0.5, 1)

    args = ap.parse_args()

    def gen(name):
        mean = getattr(args, f"{name}_mean")
        sigma = getattr(args, f"{name}_sigma")
        xmin = getattr(args, f"{name}_min")
        xmax = getattr(args, f"{name}_max")
        return limgauss(mean, sigma, xmin, xmax)

    for i in range(args.num):
        title = f"Cut{i}"
        cut_str = ",".join([f"{cut}={gen(cut)}"
                            for cut in cuts])
        print(f"{title} {cut_str}")


if __name__ == '__main__':
    main()
