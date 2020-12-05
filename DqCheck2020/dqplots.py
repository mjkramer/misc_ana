import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from root_pandas import read_root

from util import dets_for_stage2_file


class DqPlotter:
    def __init__(self, stage2_pbp_file, drl_file):
        self.hall = int(stage2_pbp_file.split(".")[-3][2])
        self.dets = dets_for_stage2_file(stage2_pbp_file)

        self.df_results = read_root(stage2_pbp_file, "results")
        self.df_ibds = {det: read_root(stage2_pbp_file, f"ibd_AD{det}")
                        for det in self.dets}
        self.df_run2day = pd.read_csv(drl_file, sep=r"\s+", header=None,
                                      names=["day", "hall", "runno", "fileno"])

        self.livetimes = self.df_results.query(f"detector == {self.dets[0]}")[
            "livetime_s"].values / (24*3600)

        assert self.df_results["seq"].is_monotonic
        self.days = self.df_results["seq"].unique()

    def do_plot(self, yss, title, yerrs=None):
        fig, axes = plt.subplots(2, 1, sharex=True,
                                 gridspec_kw={"height_ratios": [3, 1]})

        markersize = 2.5

        for i, det in enumerate(self.dets):
            yerr = yerrs[i] if yerrs else None
            axes[0].errorbar(self.days, yss[i], yerr=yerr, fmt="o",
                             ms=markersize, label=f"AD{det}")

        axes[0].set_title(f"{title} (EH{self.hall})")
        axes[0].legend()

        axes[1].plot(self.days, self.livetimes, "ko", ms=markersize)
        axes[1].set_xlabel("Days since 2011 Dec 24")
        axes[1].set_ylabel("Livetime[d]")

        fig.tight_layout()

        return fig, axes

    def results_vals(self, column):
        return [self.df_results.query(f"detector == {det}")[column].values
                for det in self.dets]

    def plot_veto_eff(self):
        yss = self.results_vals("vetoEff")
        yerrs = [0.0005 * ys / np.sqrt(self.livetimes)
                 for ys in yss]
        print(yss)
        print(yerrs)
        return self.do_plot(yss, "Muon veto efficiency", yerrs=yerrs)
