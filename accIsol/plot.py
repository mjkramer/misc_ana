import matplotlib.pyplot as plt
import pandas as pd

def read_results():
    return pd.read_csv("tables/results.txt", sep=r"\s+")

def _plot_seq(df, outer, middle, inner, site=1, det=1, day=1):
    df = df.query(f"{det} == det")
    xss = [[] for _ in range(4)]
    yss = [[] for _ in range(4)]
    sortuniq = lambda ser: sorted(ser.unique())
    j = 0
    for ov in sortuniq(df[outer]):
        for mv in sortuniq(df[middle]):
            for i, iv in enumerate(sortuniq(df[inner])):
                q = f"{outer} == {ov} and {middle} == {mv} and {inner} == {iv}"
                xss[i].append(j)
                yss[i].append(df.query(q).iloc[0].acc_day)
                j += 1

    labels = [f"{inner} = {iv}" for iv in sortuniq(df[inner])]

    for i in range(len(xss)):
        plt.plot(xss[i], yss[i], 'o', label=labels[i])

    plt.legend()
    plt.ylabel("Acc/day")
    plt.title(f"EH{site}-AD{det}, day {day}")

def plot_seq(df, code=312, **kwargs):
    # 123 -> [1, 2, 3]
    keys = [code // 100, code % 100 // 10, code % 10]
    cols = ["usec_before", "usec_after", "emin_after"]
    args = [cols[k-1] for k in keys]
    return _plot_seq(df, *args, **kwargs)
