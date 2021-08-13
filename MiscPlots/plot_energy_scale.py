#!/usr/bin/env python3

from datetime import datetime, timedelta
import os

import pandas as pd

from DBConn import DBConn


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
        self.daylister = DayLister()

    def pe_evis(self, site, det, when):
        sitemask = 4 if site == 3 else site

        query = f"""SELECT peevis FROM EnergyRecon NATURAL JOIN EnergyReconVld
        WHERE task=1 AND simmask=1 AND sitemask={sitemask} AND subsite={det}
        AND timestart <= '{when}'
        ORDER BY versiondate DESC LIMIT 1"""

        return self.db.execute(query).fetchone()[0]

    def dump(self, fname="data/energy_scales.csv"):
        def gen_data():
            for site in [1, 2, 3]:
                for det in [1, 2, 3, 4] if site == 3 else [1, 2]:
                    days = self.daylister.days_for(site, det)
                    for day in days:
                        day0 = datetime(2011, 12, 24)
                        absday = day0 + timedelta(days=day)
                        escale = self.pe_evis(site, det, absday)
                        print((site, det, day, escale), flush=True)
                        yield {"site": site, "det": det, "day": day,
                               "escale": escale}

        data = pd.DataFrame(gen_data())
        data.to_csv(fname, index=False)


if __name__ == '__main__':
    table = EnergyScaleTable()
    table.dump()
