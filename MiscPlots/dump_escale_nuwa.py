#!/usr/bin/env python2.7

from __future__ import print_function

from datetime import timedelta
from itertools import chain
from multiprocessing import Pool
import os
import sys

from Gaudi.Configuration import ApplicationMgr
from GaudiPython import AppMgr, gbl

from util27 import SITEDETS, DAY0, DayLister, dictlistsort

DATAFILE = "data/escale_nuwa.csv"

# unbuffer
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

Detector = gbl.DayaBay.Detector  # without this, can't access gbl.Site
Site = gbl.Site

theApp = ApplicationMgr()
theApp.ExtSvc.append("DybDetCalibSvc/DybDetCalibSvc")

appMgr = AppMgr()
appMgr.initialize()

detCalibSvc = appMgr.service("DybDetCalibSvc", "IDetCalibSvc")


def get_escale(site, det, when):
    sitemask = 4 if site == 3 else site

    ts = gbl.TimeStamp(when.year, when.month, when.day,
                       when.hour, when.minute, when.second)

    ctx = gbl.Context(sitemask, gbl.SimFlag.kData, ts, det)
    sm_escale = gbl.ServiceMode(ctx, 1)
    data = detCalibSvc.detEnergyReconData(sm_escale)

    return data.m_PeEvis


# put args in a tuple since py2.7's Pool doesn't have starmap
def get_rows(sitedet):
    site, det = sitedet
    prevdays = DayLister().days_for(site, det)

    def gen():
        for prevday in prevdays:
            day = prevday + 1
            absday = DAY0 + timedelta(days=day)
            try:
                escale = get_escale(site, det, absday)
                print(day, site, det, escale)
                yield {"day": day, "site": site, "det": det,
                       "escale": escale}
            except Exception:
                print("FAIL", day, site, det)

    return list(gen())


def dump(fname=DATAFILE):
    results = Pool(processes=8).map(get_rows, SITEDETS)

    data = list(chain(*results))
    dictlistsort(data, ["day", "site", "det"])

    outf = open(fname, "w")
    outf.write("day,site,det,escale\n")

    for row in data:
        outf.write("%d,%d,%d,%f\n" %
                   (row["day"], row["site"], row["det"], row["escale"]))


if __name__ == '__main__':
    dump()
