#!/usr/bin/env python3

from datetime import timedelta
from itertools import chain
from multiprocessing import Pool

import matplotlib.pyplot as plt
import pandas as pd

from DBConn import DBConn
from util import SITEDETS, DAY0, DayLister


DBNAME = "offline_db_ihep"
DATAFILE = "data/energy_scale.csv"


def get_energy_scale(db: DBConn, site, det, when):
    sitemask = 4 if site == 3 else site

    query = f"""SELECT peevis FROM EnergyRecon NATURAL JOIN EnergyReconVld
    WHERE task=1 AND simmask=1 AND sitemask={sitemask} AND subsite={det}
    AND timestart <= '{when}'
    ORDER BY versiondate DESC LIMIT 1"""

    return db.execute(query).fetchone()[0]


# Should be internal to 'dump', but we get an error
# ("can't pickle local function")
def get_rows(site, det):
    db = DBConn(DBNAME)
    days = DayLister().days_for(site, det)

    def gen():
        for day in days:
            absday = DAY0 + timedelta(days=day)
            escale = get_energy_scale(db, site, det, absday)
            print((day, site, det, escale), flush=True)
            yield {"day": day, "site": site, "det": det,
                   "escale": escale}

    return list(gen())


def dump(fname=DATAFILE):
    results = Pool(processes=8).starmap(get_rows, SITEDETS)

    data = pd.DataFrame(chain(*results))
    data.sort_values(["day", "site", "det"], inplace=True)
    data.to_csv(fname, index=False)


def plot_energy_scale(fname=DATAFILE, **plotargs):
    data = pd.read_csv(fname)

    fig, ax = plt.subplots()

    for site, det in SITEDETS:
        label = f"EH{site}-AD{det}"
        subdata = data.query(f"site == {site} and det == {det}")
        days = [DAY0 + timedelta(days=day)
                for day in subdata["day"]]
        ax.plot(days, subdata["escale"], "o", label=label, ms=2, **plotargs)

    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("PE/MeV")
    ax.set_title("AdSimple energy scale")
    fig.tight_layout()

    fig.savefig("gfx/energy_scale.pdf")

    return fig, ax


if __name__ == '__main__':
    dump(DATAFILE)
