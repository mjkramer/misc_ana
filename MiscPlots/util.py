#!/usr/bin/env python3

import ROOT as R

from datetime import datetime
import os

import pandas as pd


SITEDETS = [(1, 1), (1, 2), (2, 1), (2, 2),
            (3, 1), (3, 2), (3, 3), (3, 4)]

DAY0 = datetime(2011, 12, 24)


def dets_for(hall, nADs):
    if hall == 1:
        return [2] if nADs == 7 else [1, 2]
    if hall == 2:
        return [1] if nADs == 6 else [1, 2]
    if hall == 3:
        return [1, 2, 3] if nADs == 6 else [1, 2, 3, 4]
    raise


def keep(o):
    R.SetOwnership(o, False)     # don't delete it, python!
    try:
        o.SetDirectory(R.gROOT)  # don't delete it, root!
        # o.SetDirectory(0)
    except Exception:
        pass                     # unless you weren't going to anyway
    return o


class DayLister:
    def __init__(self):
        fithome = os.environ["LBNL_FIT_HOME"]
        path = f"{fithome}/ReactorPowerCalculator/dbd_livetime_P17B.txt"
        self.df = pd.read_csv(path, sep=r"\s+",
                              names=["day", "site", "livetime"])

    def days_for(self, site, det):
        sitedays = self.df.query(f"site == {site}")["day"]
        daymin, daymax = self._minmax_days(site, det)
        return [day for day in sitedays
                if daymin <= day <= daymax]

    def _minmax_days(self, site, det):
        if (site, det) in [(2, 2), (3, 4)]:
            return (218, 2076)
        elif (site, det) == (1, 1):
            return (0, 1824)
        else:
            return (0, 2076)
