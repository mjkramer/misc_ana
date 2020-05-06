import ROOT as R
import numpy as np

import os

nS2T = 31
nDM2 = 31
s2t_min = 0.07
s2t_max = 0.10
dm2_min = 2.1e-3
dm2_max = 2.8e-3

BASE = "/global/homes/m/mkramer/mywork/ThesisAnalysis/samples"
CONFIGS = {"2e5_pe__300_ms": "beda.tmp23",
           "2e5_pe__500_ms": "beda.tmp25",
           "4e5_pe__300_ms": "beda.tmp43",
           "4e5_pe__500_ms": "beda.tmp45"}

cn = list(CONFIGS.keys())[0]


def fit_file(configname):
    rel = "ShapeFit/fit_result_files/fit_shape_2d_2017Model_P17B_LBNL.root"
    return os.path.join(BASE, CONFIGS[configname], rel)


def read_fit_file(fname):
    f = R.TFile(fname)

    t = f.Get("tr_fit")
    t.GetEntry(0)
    s2t_best = t.GetLeaf("s2t_min").GetValue()
    dm2_best = t.GetLeaf("dm2_min").GetValue()
    # chi2_min_from_tree = t.GetLeaf("chi2_min").GetValue()

    chi2_best = 1e10
    h_chi2_map = f.Get("h_chi2_map")
    chi2_map = np.zeros([nDM2, nS2T])

    for idm in range(nDM2):
        for is2 in range(nS2T):
            chi2_map[idm][is2] = h_chi2_map.GetBinContent(is2 + 1, idm + 1)
            if chi2_map[idm][is2] < chi2_best:
                chi2_best = chi2_map[idm][is2]

    sin22t13 = np.zeros([nS2T])
    dm2 = np.zeros([nDM2])

    for step in range(nS2T):
        sin22t13[step] = (s2t_max - s2t_min) * step * 1. / (nS2T - 1) + s2t_min

    for step_dm2 in range(nDM2):
        dm2[step_dm2] = \
            (dm2_max - dm2_min) * step_dm2 * 1. / (nDM2 - 1) + dm2_min

    chi2_s2t = np.zeros([nS2T])
    chi2_dm2 = np.zeros([nDM2])

    chi2_best = 0

    projected_chi2 = 1e10
    is2_best = 0
    for idm in range(nDM2):
        for is2 in range(nS2T):
            if chi2_map[idm][is2] < projected_chi2:
                projected_chi2 = chi2_map[idm][is2]
                is2_best = is2
        chi2_dm2[idm] = chi2_map[idm][is2_best] - chi2_best

    projected_chi2 = 1e10
    idm_best = 0
    for is2 in range(nS2T):
        for idm in range(nDM2):
            if chi2_map[idm][is2] < projected_chi2:
                projected_chi2 = chi2_map[idm][is2]
                idm_best = is2
        chi2_s2t[is2] = chi2_map[idm_best][is2] - chi2_best

    for i in range(nS2T - 1):
        if chi2_s2t[i] > 1 and chi2_s2t[i + 1] < 1:
            allowed_min_s = \
                ((1 - chi2_s2t[i + 1]) * sin22t13[i] +
                 (chi2_s2t[i] - 1) * sin22t13[i + 1]) / \
                (chi2_s2t[i] - chi2_s2t[i + 1])

        if chi2_s2t[i] < 1 and chi2_s2t[i + 1] > 1:
            allowed_max_s = \
                ((1 - chi2_s2t[i + 1]) * sin22t13[i] +
                 (chi2_s2t[i] - 1) * sin22t13[i + 1]) / \
                (chi2_s2t[i] - chi2_s2t[i + 1])

    for i in range(nDM2 - 1):
        if chi2_dm2[i] > 1 and chi2_dm2[i + 1] < 1:
            allowed_min_d = \
                ((1 - chi2_dm2[i + 1]) * dm2[i] +
                 (chi2_dm2[i] - 1) * dm2[i + 1]) / \
                (chi2_dm2[i] - chi2_dm2[i + 1])

        if chi2_dm2[i] < 1 and chi2_dm2[i + 1] > 1:
            allowed_max_d = \
                ((1 - chi2_dm2[i + 1]) * dm2[i] +
                 (chi2_dm2[i] - 1) * dm2[i + 1]) / \
                (chi2_dm2[i] - chi2_dm2[i + 1])

    return [(allowed_min_s, s2t_best, allowed_max_s),
            (allowed_min_d, dm2_best, allowed_max_d)]


def report():
    for cn in CONFIGS.keys():
        print(f"{cn}:")
        [(sL, s0, sH), (dL, d0, dH)] = read_fit_file(fit_file(cn))
        print("s22t13: %.3g + %.3g - %.3g" % (s0, sH, sL))
        print("dm2: %.3g + %.3g - %.3g" % (d0, dH, dL))
        print()
