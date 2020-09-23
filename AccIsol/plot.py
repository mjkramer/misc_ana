import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# from mpl_toolkits.axes_grid.parasite_axes import SubplotHost
from mpl_toolkits.axisartist import SubplotHost
import pandas as pd

def read_results():
    return pd.read_csv("tables/results.txt", sep=r"\s+")

def _plot_seq(df, outer, middle, inner, site=1, det=1, day=1, col='acc_day'):
    fig = plt.figure()
    ax1 = SubplotHost(fig, 111)
    fig.add_subplot(ax1)

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
                yss[i].append(df.query(q).iloc[0][col])
                j += 1

    labels = [f"{inner} = {iv}" for iv in sortuniq(df[inner])]

    for i in range(len(xss)):
        ax1.plot(xss[i], yss[i], 'o', label=labels[i])

    ax1.set_xticks([1.5, 5.5, 9.5,  13.5, 17.5, 21.5,
                    25.5, 29.5, 33.5,  37.5, 41.5, 45.5])
    ax1.set_xticklabels(4*[f"{mv}" for mv in sortuniq(df[middle])])
    ax1.yaxis.set_label_text(col)

    ax2 = ax1.twiny()
    offset = 0, -25
    new_axisline = ax2.get_grid_helper().new_fixed_axis
    ax2.axis["bottom"] = new_axisline(loc="bottom", axes=ax2, offset=offset)
    # ax2.axis["top"].set_visible(False)
    # ax2.set_xticks([5.5, 17.5, 29.5, 41.5])
    # ax2.set_xticks([0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48])
    ax2.set_xticks([0, 12, 24, 36, 48])
    ax2.xaxis.set_major_formatter(ticker.NullFormatter())
    ax2.xaxis.set_minor_locator(ticker.FixedLocator([5.5, 17.5, 29.5, 41.5]))
    ax2.xaxis.set_minor_formatter(ticker.FixedFormatter([f"{ov}" for ov in sortuniq(df[outer])]))

    plt.legend()
    # plt.ylabel("Acc/day")
    plt.title(f"Calculated {col} vs. singles isolation cuts, EH{site}-AD{det}, day {day}")

def plot_seq(df, code=312, **kwargs):
    # 123 -> [1, 2, 3]
    keys = [code // 100, code % 100 // 10, code % 10]
    cols = ["usec_before", "usec_after", "emin_after"]
    args = [cols[k-1] for k in keys]
    return _plot_seq(df, *args, **kwargs)
