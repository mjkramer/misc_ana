#!/usr/bin/env python3

import argparse

import ROOT as R


def remove_AD_txt(t13file, detno):
    # In keeping with the 6/7AD period conventions, don't zero-out these rows.
    # Probably not necessary but might save us a divide-by-zero.
    rows2skip = [8]

    in_lines = open(t13file).readlines()
    f_out = open(t13file, "w")

    headers_remaining = 4       # treat date/time row as header
    for line in in_lines:
        if line.strip().startswith("#"):
            f_out.write(line)
            continue

        if headers_remaining > 0:
            f_out.write(line)
            headers_remaining -= 1
            continue

        words = line.strip().split()
        if int(words[1]) not in rows2skip:
            words[1 + detno] = "0"
        f_out.write("\t".join(words) + "\n")


def remove_AD_prompt(promptfile, site, det):
    f = R.TFile(promptfile, "UPDATE")
    for key in [f"h_ibd_eprompt_inclusive_eh{site}_ad{det}",
                f"h_ibd_eprompt_fine_inclusive_eh{site}_ad{det}"]:
        h = f.Get(key)
        h.Reset()
        h.Write()


def remove_AD_acc(accfile, site, det):
    f = R.TFile(accfile, "UPDATE")
    for key in [f"h_accidental_eprompt_inclusive_eh{site}_ad{det}",
                f"h_accidental_eprompt_fine_inclusive_eh{site}_ad{det}"]:
        h = f.Get(key)
        h.Reset()
        h.Write()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("detno", type=int, help="1-8")
    ap.add_argument("--txt", action="store_true")
    ap.add_argument("--prompt", action="store_true")
    ap.add_argument("--acc", action="store_true")
    args = ap.parse_args()

    site = [1, 1, 2, 2, 3, 3, 3, 3][args.detno - 1]
    det = [1, 2, 1, 2, 1, 2, 3, 4][args.detno - 1]

    for nADs in [6, 8, 7]:
        if args.txt:
            t13file = f"{args.directory}/Theta13-inputs_P17B" + \
                f"_inclusive_{nADs}ad.txt"
            remove_AD_txt(t13file, args.detno)

        if args.prompt:
            promptfile = f"{args.directory}/ibd_eprompt_shapes_{nADs}ad.root"
            remove_AD_prompt(promptfile, site, det)

        if args.acc:
            accfile = f"{args.directory}/accidental_eprompt_shapes" + \
                f"_{nADs}ad.root"
            remove_AD_acc(accfile, site, det)


if __name__ == '__main__':
    main()
