import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from root_pandas import read_root

from util import dets_for_stage2_file


class DqPlotter:
    def __init__(self, stage2_pbp_file, drl_file="data/dbd_runlist_p20a.txt",
                 fits_dir="data/fits"):
        self.hall = int(stage2_pbp_file.split(".")[-3][2])
        self.dets = dets_for_stage2_file(stage2_pbp_file)

        self.df_results = read_root(stage2_pbp_file, "results") \
            .rename(columns={"seq": "day"})

        self.df_run2day = pd.read_csv(drl_file, sep=r"\s+", header=None,
                                      names=["day", "hall", "runNo", "fileNo"],
                                      index_col=['runNo', 'fileNo'])
        self.df_ibds = {det: read_root(stage2_pbp_file, f"ibd_AD{det}")
                        .join(self.df_run2day, on=['runNo', 'fileNo'])
                        for det in self.dets}

        self.livetimes = self.df_results.query(f"detector == {self.dets[0]}")[
            "livetime_s"].sort_index().values / (24*3600)

        assert self.df_results["day"].is_monotonic
        self.days = self.df_results["day"].unique()

        self.df_peaks = {}
        for peak in ["k40", "tl208"]:
            ndet = 4 if self.hall == 3 else 2
            cols = [f"valAD{n}" for n in range(1, ndet+1)]
            cols_err = [f"errAD{n}" for n in range(1, ndet+1)]
            df_vals = pd.read_csv(f"{fits_dir}/{peak}.eh{self.hall}.csv",
                                  sep=r"\s+",
                                  names=["day"]+cols, index_col="day")
            df_errs = pd.read_csv(f"{fits_dir}/{peak}_err.eh{self.hall}.csv",
                                  sep=r"\s+",
                                  names=["day"]+cols_err, index_col="day")
            self.df_peaks[peak] = df_vals.join(df_errs)

    def do_plot(self, yss, title, tag, yerrs=None):
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
        fig.savefig(f"gfx/{tag}.eh{self.hall}.pdf")

        return fig, axes

    def results_vals(self, column):
        return [self.df_results.query(f"detector == {det}")[column]
                .sort_index().values
                for det in self.dets]

    def fudged_errors(self, yss, frac_err):
        return [frac_err * ys / np.sqrt(self.livetimes)
                for ys in yss]

    def plot_veto_eff(self):
        yss = self.results_vals("vetoEff")
        yerrs = self.fudged_errors(yss, 0.0005)
        return self.do_plot(yss, "Muon veto efficiency", "vetoEff",
                            yerrs=yerrs)

    def plot_dmc_eff(self):
        yss = self.results_vals("dmcEff")
        yerrs = self.fudged_errors(yss, 0.00005)
        return self.do_plot(yss, "Multiplicity cut efficiency", "dmcEff",
                            yerrs=yerrs)

    def plot_acc_rate(self):
        yss = self.results_vals("accDaily")
        yerrs = self.results_vals("accDailyErr")
        return self.do_plot(yss, "Accidentals per day", "acc", yerrs=yerrs)

    def rate_with_error(self, rate_col, count_col):
        rates = self.results_vals(rate_col)
        counts = self.results_vals(count_col)
        eff_veto = self.results_vals("vetoEff")
        eff_mult = self.results_vals("dmcEff")
        errs = [np.sqrt(counts[i]) /
                (self.livetimes * 3600*24 * eff_veto[i] * eff_mult[i])
                for i in range(len(counts))]
        return rates, errs

    def plot_preMuon_rate(self):
        yss, yerrs = self.rate_with_error("preMuonHz", "nPreMuons")
        return self.do_plot(yss, "Pre-muon rate [Hz]", "preMuonHz",
                            yerrs=yerrs)

    def plot_promptLike_rate(self):
        yss, yerrs = self.rate_with_error("promptLikeHz", "nPromptLikeSingles")
        return self.do_plot(yss, "Prompt-like rate [Hz]", "promptLikeHz",
                            yerrs=yerrs)

    def plot_delayedLike_rate(self):
        yss, yerrs = self.rate_with_error("delayedLikeHz",
                                          "nDelayedLikeSingles")
        return self.do_plot(yss, "Delayed-like rate [Hz]", "delayedLikeHz",
                            yerrs=yerrs)

    def plot_plusLike_rate(self):
        yss, yerrs = self.rate_with_error("plusLikeHz", "nPlusLikeSingles")
        return self.do_plot(yss, "Plus-like rate [Hz]", "plusLikeHz",
                            yerrs=yerrs)

    def ibd_vals(self, column):
        yss, yerrs = [], []
        for df in self.df_ibds.values():
            gb = df.groupby("day")
            means = gb.mean()
            uncs = gb.std() / np.sqrt(gb.count())
            yss.append(means[column].sort_index().values)
            yerrs.append(uncs[column].sort_index().values)
        return yss, yerrs

    def ibd_rate(self):
        yss, yerrs = [], []
        for df in self.df_ibds.values():
            counts = df.groupby("day").count()["eP"]  # eP or any col
            times = self.df_results.set_index("day")["livetime_s"] \
                                   .drop_duplicates() / (3600*24)
            yss.append((counts / times).sort_index().values)
            yerrs.append((np.sqrt(counts) / times).sort_index().values)
        return yss, yerrs

    def plot_ibd_dt(self):
        yss, yerrs = self.ibd_vals("dt_us")
        return self.do_plot(yss, "IBD dt [us]", "dt", yerrs=yerrs)

    def plot_ibd_ePrompt(self):
        yss, yerrs = self.ibd_vals("eP")
        return self.do_plot(yss, "IBD mean prompt energy", "ePrompt",
                            yerrs=yerrs)

    def plot_ibd_eDelayed(self):
        yss, yerrs = self.ibd_vals("eP")
        return self.do_plot(yss, "IBD mean delayed energy", "eDelayed",
                            yerrs=yerrs)

    def plot_ibd_rate(self):
        yss, yerrs = self.ibd_rate()
        return self.do_plot(yss, "IBD candidate daily rate", "ibdRate",
                            yerrs=yerrs)

    def peak_fits(self, peakname):
        df = self.df_peaks[peakname]
        yss = [df[f"valAD{det}"].sort_index().values
               for det in self.dets]
        yerrs = [df[f"errAD{det}"].sort_index().values
                 for det in self.dets]
        return yss, yerrs

    def plot_k40(self):
        yss, yerrs = self.peak_fits("k40")
        return self.do_plot(yss, "K40 peak", "k40", yerrs=yerrs)

    def plot_tl208(self):
        yss, yerrs = self.peak_fits("tl208")
        return self.do_plot(yss, "Tl208 peak", "tl208", yerrs=yerrs)
