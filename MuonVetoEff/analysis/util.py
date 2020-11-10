from glob import glob
import os

import pandas as pd


T13_ROWS = {
    "obs_evt": 1,
    "livetime": 2,
    "veto_eff": 3,
    "mult_eff": 4,
    "tot_bkg": 9,
    "li9_bkg": 13,
}


def read_theta13_file(fname):
    "Returns {rownum: [valAD1, ..., valAD8]}"
    result = {}
    headers_remaining = 3

    for line in open(fname):
        line = line.strip()

        if line.startswith("#") or not line:
            continue

        if headers_remaining > 0:
            headers_remaining -= 1
            continue

        words = line.split()
        rownum = int(words[1])
        if rownum == 0:         # timestamps etc
            continue
        vals = map(float, words[2:])
        result[rownum] = list(vals)

    return result


def dump_quantity(study, rowname, nADs=8):
    data = []

    for direc in glob(f"fit_results/{study}/*"):
        parts = os.path.basename(direc).split("_")
        cut_pe = float(parts[-2][:-2])
        time_s = float(parts[-1][:-1])

        t13_file = f"{direc}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        t13_data = read_theta13_file(t13_file)
        t13_row = t13_data[T13_ROWS[rowname]]
        vals = {f"AD{i+1}": t13_row[i] for i in range(8)}
        row = {"cut_pe": cut_pe, "time_s": time_s, **vals}
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(f"summaries/{study}.{rowname}.{nADs}ad.csv")
