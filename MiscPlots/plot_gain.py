#!/usr/bin/env python3

from datetime import timedelta
from itertools import chain
from multiprocessing import Pool

import matplotlib.pyplot as plt
import pandas as pd

from DBConn import DBConn
from util import SITEDETS, DAY0, DayLister


DBNAME = "offline_db_ihep"
DATAFILE = "data/gain_nuwa.csv"

# TWOINCH_IDS = {
#     (1, 1): (16847361, 16847375),
#     (1, 2): 
# }


# def get_cablemap(db: DBConn, site, det, when):
#     sitemask = 4 if site == 3 else site

#     query = f"""SELECT seqno FROM CableMapVld
#     WHERE simmask=1 AND sitemask={sitemask} AND subsite={det}
#     AND timestart <= '{when}'
#     ORDER BY versiondate DESC LIMIT 1"""

#     seqno = db.execute(query).fetchone()[0]

#     query = f"""SELECT channelid, sensorid FROM CableMap
#     WHERE seqno={seqno}"""

#     rows = db.execute(query).fetchall()
#     return dict(rows)

# def get_gain(db: DBConn, site, det, when):
#     sitemask = 4 if site == 3 else site

#     query = f"""SELECT seqno FROM CalibPmtFineGainVld
#     WHERE simmask=1 AND sitemask={sitemask} AND subsite={det}
#     AND timestart <= '{when}'
#     ORDER BY versiondate DESC LIMIT 1"""

#     seqno = db.execute(query).fetchone()[0]

#     query = f"""SELECT channelid, spehigh FROM CalibPmtFineGain
#     WHERE seqno={seqno}"""

#     rows = db.execute(query).fetchall()
#     cmap = get_cablemap(db, site, det, when)
#     tot, n = 0, 0

#     for channelid, spehigh in rows:
#         if spehigh != 19:
#             pass


# # Should be internal to 'dump', but we get an error
# # ("can't pickle local function")
# def get_rows(site, det):
#     db = DBConn(DBNAME)
#     days = DayLister().days_for(site, det)

#     def gen():
#         for day in days:
#             absday = DAY0 + timedelta(days=day)
#             gain = get_gain(db, site, det, absday)
#             print((day, site, det, gain), flush=True)
#             yield {"day": day, "site": site, "det": det,
#                    "gain": gain}

#     return list(gen())


# def dump(fname=DATAFILE):
#     results = Pool(processes=8).starmap(get_rows, SITEDETS)

#     data = pd.DataFrame(chain(*results))
#     data.sort_values(["day", "site", "det"], inplace=True)
#     data.to_csv(fname, index=False)


def plot_gain(fname=DATAFILE, **plotargs):
    data = pd.read_csv(fname)

    fig, ax = plt.subplots()

    for site, det in SITEDETS:
        label = f"EH{site}-AD{det}"
        subdata = data.query(f"site == {site} and det == {det}")
        days = [DAY0 + timedelta(days=day)
                for day in subdata["day"]]
        ax.plot(days, subdata["gain"], "o", label=label, ms=2, **plotargs)

    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("ADC/PE")
    ax.set_title("AD-averaged gain")
    fig.tight_layout()

    fig.savefig("gfx/gain_nuwa.pdf")

    return fig, ax


# if __name__ == '__main__':
#     dump(DATAFILE)
