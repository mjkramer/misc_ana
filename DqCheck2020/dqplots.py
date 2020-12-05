import matplotlib.pyplot as plt
import pandas as pd
from root_pandas import read_root

from util import dets_for_stage2_file


class DqPlotter:
    def __init__(self, stage2_pbp_file, drl_file):
        self.hall = int(stage2_pbp_file.split(".")[-3][2])
        self.df_results = read_root(stage2_pbp_file, "results")
        self.df_ibds = {det: read_root(stage2_pbp_file, f"ibd_AD{det}")
                        for det in dets_for_stage2_file(stage2_pbp_file)}
        self.df_run2day = pd.read_csv(drl_file, sep=r"\s+", header=None,
                                      names=["day", "hall", "runno", "fileno"])

    def do_plot(self, ys, title, det, yerr=None):
        fig, axes = plt.subplots(2, 1, sharex=True,
                                 gridspec_kw={"height_ratios": [3, 1]})
        sub_df = self.df_results.query(f"detector == {det}")
        xs = sub_df["seq"]

        axes[0].errorbar(xs, ys, yerr=yerr, fmt="o")
        axes[1].plot(xs, sub_df["livetime_s"] / (24*3600), "o")

        axes[0].set_title(f"{title} (EH{self.hall}-AD{det})")
        axes[1].set_xlabel("Days since 2011 Dec 24")
        axes[1].set_ylabel("Livetime[s]")

    def plot_from_results(self, column, title, det):
        ys = self.df_results.query(f"detector == {det}")[column]
        return self.do_plot(ys, title, det)

    def plot_veto_eff(self, det):
        return self.plot_from_results("vetoEff", "Muon veto efficiency", det)
