from glob import glob
import os

import pandas as pd
import ROOT as R

from plot_fit_results import read_study

def dump_fit_results(study):
    df = read_study(study)
    df.to_csv(f"summaries/{study}.csv")
