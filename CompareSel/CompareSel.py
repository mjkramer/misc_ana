import matplotlib.pyplot as plt
from itertools import islice
from functools import lru_cache
import os

plt.rcParams["figure.figsize"] = [8, 6]
plt.rcParams["axes.labelsize"] = "x-large"
plt.rcParams["xtick.labelsize"] = "large"
plt.rcParams["ytick.labelsize"] = "large"
plt.rcParams["axes.titlesize"] = "xx-large"
plt.rcParams["legend.fontsize"] = "xx-large"

ROWS = {
    1: 'NumIBDs',
    2: 'Livedays',
    3: 'VetoEff',
    4: 'MultEff',
    9: 'DailyTotBkg',
    11: 'DailyAcc',
    13: 'DailyLi9',
    15: 'DailyFastN',
    17: 'DailyAmC',
    19: 'DailyAlphaN'
}

PATHSPECS = {
    'LBNL': '/global/u2/m/mkramer/mywork/ThesisAnalysis/samples/beda.mine/example/LBNL/Theta13-inputs_P17B_inclusive_%s_LBNL.txt',
    'Matt': '/global/u2/m/mkramer/mywork/ThesisAnalysis/samples/beda.mine/example/yolo2/Theta13-inputs_P17B_inclusive_%s.txt'
}

SPLIT_NEAR_FAR = ['NumIBDs']
SUM_PHASES = ['NumIBDs', 'Livedays']

def path_of(selname, phasename):
    assert selname in PATHSPECS
    assert phasename in ['6ad', '8ad', '7ad']
    return PATHSPECS[selname] % phasename

def has_err(rowname):
    return rowname.startswith('Daily')

@lru_cache()
def get_data(selname, phasename):
    fname = path_of(selname, phasename)
    result = {}

    def not_comment(line):
        return not line.startswith('#')

    lines = filter(not_comment, open(fname))
    lines = islice(lines, 3, None)  # don't want first 3 data lines

    for line in lines:
        parts = line.split()
        rowcode = int(parts[1])
        if rowcode in ROWS:
            rowname = ROWS[rowcode]
        elif rowcode-1 in ROWS and has_err(ROWS[rowcode-1]):
            rowname = ROWS[rowcode-1] + 'Unc'
        else:
            continue
        vals = [float(_) for _ in parts[2:10]]
        result[rowname] = vals

    return result

def livetime(idet, selname, phasename):
    data = get_data(selname, phasename)
    return data['Livedays'][idet]

def get_xy(rowname, selname, phasename=None, halls='both', offset=0):
    xmin, xmax = (0, 3) if halls == 'near' \
        else (4, 7) if halls == 'far' \
             else (0, 7)

    xs = [_ + offset for _ in range(8)]
    ys = [0] * 8
    yerr = [0] * 8 if has_err(rowname) else None
    phases = ['6ad', '8ad', '7ad'] if phasename is None else [phasename]

    weightsum = [0] * 8
    for phase in phases:
        data = get_data(selname, phase)
        ys0 = data[rowname]
        yerr0 = data[rowname+'Unc'] if yerr is not None else None
        for i in range(8):
            weight = 1 if rowname in SUM_PHASES else livetime(i, selname, phase)
            weightsum[i] += weight
            ys[i] += ys0[i] * weight
            if yerr is not None:
                yerr[i] += yerr0[i] * weight

    if rowname in SUM_PHASES:
        weightsum = [1] * 8

    xs0, ys0, yerr0 = xs, ys, yerr
    xs, ys, yerr = [], [], [] if yerr0 else None
    for i in range(8):
        if i < xmin or i > xmax:
            continue
        if ys0[i] != 0:
            xs.append(xs0[i])
            ys.append(ys0[i] / weightsum[i])
            if yerr0 is not None:
                yerr.append(yerr0[i] / weightsum[i])

    return xs, ys, yerr

def plot(ax, rowname, selname, phasename=None, halls='both', offset=0):
    xs, ys, yerr = get_xy(rowname, selname, phasename=phasename, halls=halls, offset=offset)

    ax.errorbar(xs, ys, yerr=yerr, fmt='o', label=selname)

    nearticks, farticks = [0, 1, 2, 3], [4, 5, 6, 7]
    neardets, fardets = ['AD1', 'AD2', 'AD3', 'AD8'], ['AD4', 'AD5', 'AD6', 'AD7']
    xticks = nearticks if halls == 'near' else (farticks if halls == 'far' else nearticks + farticks)
    xdets = neardets if halls == 'near' else (fardets if halls == 'far' else neardets + fardets)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xdets)
    ax.set_xlim(xticks[0] - 0.5, xticks[-1] + 0.5)
    phasetitle = f', {phasename.upper()} period' if phasename else ''
    halltitle = (f', {halls} hall' if halls != 'both' else '') + \
        ('s' if halls == 'near' else '')
    ax.set_title(f'{rowname}{halltitle}{phasetitle}')

def compare(rowname, phasename=None, halls='both'):
    fig, ax = plt.subplots()
    for i, selname in enumerate(PATHSPECS):
        offset = i * 0.2 - 0.1
        plot(ax, rowname, selname, phasename=phasename, halls=halls, offset=offset)
    fig.legend()
    return fig

def compare_all(split_phases=False):
    os.system('mkdir -p gfx')
    phases = ['6ad', '7ad', '8ad'] if split_phases else [None]
    tag = 'split' if split_phases else 'comb'
    with open(f'CompareSel_{tag}_gfx.org', 'w') as f:
        for rowname in ROWS.values():
            for phasename in phases:
                hallsets = ['near', 'far'] if rowname in SPLIT_NEAR_FAR else ['both']
                for hallset in hallsets:
                    phname = phasename if phasename else 'AllPhases'
                    fname = f'gfx/compare_{rowname}_{phname}_{hallset}.png'
                    fig = compare(rowname, phasename, halls=hallset)
                    # fig.show()      # b/c matplotlib is stupid
                    fig.savefig(fname)
                    f.write(f'[[file:{fname}]]\n')
                    # plt.pause(0.05)  # b/c matplotlib is stupid
                    # os.system(f'mogrify -negate {fname}')

compare_all(split_phases=False)
compare_all(split_phases=True)

compare('NumIBDs', halls='far');
