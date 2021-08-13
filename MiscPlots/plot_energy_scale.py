#!/usr/bin/env python3

from datetime import datetime, timedelta
from itertools import chain
from multiprocessing import Pool
import os

import pandas as pd

from DBConn import DBConn


SITEDETS = [(1, 1), (1, 2), (2, 1), (2, 2),
            (3, 1), (3, 2), (3, 3), (3, 4)]



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


class EnergyScaleTable:
    def __init__(self, dbname="offline_db_ihep", **kwargs):
        self.db = DBConn(dbname, **kwargs)

    def pe_evis(self, site, det, when):
        sitemask = 4 if site == 3 else site

        query = f"""SELECT peevis FROM EnergyRecon NATURAL JOIN EnergyReconVld
        WHERE task=1 AND simmask=1 AND sitemask={sitemask} AND subsite={det}
        AND timestart <= '{when}'
        ORDER BY versiondate DESC LIMIT 1"""

        return self.db.execute(query).fetchone()[0]


# Should be internal to 'dump', but we get an error
# ("can't pickle local function")
def get_rows(site, det):
    table = EnergyScaleTable()
    days = DayLister().days_for(site, det)

    def gen():
        for day in days:
            day0 = datetime(2011, 12, 24)
            absday = day0 + timedelta(days=day)
            escale = table.pe_evis(site, det, absday)
            print((day, site, det, escale), flush=True)
            yield {"day": day, "site": site, "det": det,
                   "escale": escale}

    return list(gen())


def dump(fname="data/energy_scales.csv"):
    results = Pool(processes=8).starmap(get_rows, SITEDETS)

    data = pd.DataFrame(chain(*results))
    data.sort_values(["day", "site", "det"], inplace=True)
    data.to_csv(fname, index=False)


if __name__ == '__main__':
    dump("data/energy_scales_par.csv")
