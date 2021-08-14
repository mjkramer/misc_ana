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

DATAFILE = "data/gain_nuwa.csv"

# unbuffer
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

Detector = gbl.DayaBay.Detector  # without this, can't access gbl.Site
Site = gbl.Site

theApp = ApplicationMgr()
theApp.ExtSvc.append("DybPmtCalibSvc/DybPmtCalibSvc")
theApp.ExtSvc.append("DybChannelQualitySvc/DybChannelQualitySvc")
theApp.ExtSvc.append("DybCableSvc/DybCableSvc")

appMgr = AppMgr()
appMgr.initialize()

calibSvc = appMgr.service("DybPmtCalibSvc", "IPmtCalibSvc")
cqSvc = appMgr.service("DybChannelQualitySvc", "IChannelQualitySvc")
cableSvc = appMgr.service("DybCableSvc", "ICableSvc")


def avg_gain(site, det, when):
    sitemask = 4 if site == 3 else site

    ts = gbl.TimeStamp(when.year, when.month, when.day,
                       when.hour, when.minute, when.second)

    ctx = gbl.Context(sitemask, gbl.SimFlag.kData, ts, det)

    sm_calib = gbl.ServiceMode(ctx, 1)
    sm_cq = gbl.ServiceMode(ctx, 0)
    sm_cable = gbl.ServiceMode(ctx, 0)

    cq = cqSvc.channelQuality(sm_cq)

    tot, n = 0, 0

    for channelid in cq.channels():
        if cq.good(channelid):
            sensorid = cableSvc.sensor(channelid, sm_cable)
            if sensorid.isAD():
                pmtId = gbl.DayaBay.AdPmtSensor(sensorid.fullPackedData())
                if pmtId.is8inch():
                    cal = calibSvc.fineGainCalibData(channelid, sm_calib)
                    tot += cal.m_speHigh
                    n += 1

    return tot / n


# put args in a tuple since py2.7's Pool doesn't have starmap
def get_rows(sitedet):
    site, det = sitedet
    prevdays = DayLister().days_for(site, det)

    def gen():
        for prevday in prevdays:
            day = prevday + 1
            absday = DAY0 + timedelta(days=day)
            try:
                gain = avg_gain(site, det, absday)
                print(day, site, det, gain)
                yield {"day": day, "site": site, "det": det,
                       "gain": gain}
            except Exception:
                print("FAIL", day, site, det)

    return list(gen())


def dump(fname=DATAFILE):
    results = Pool(processes=8).map(get_rows, SITEDETS)

    data = list(chain(*results))
    dictlistsort(data, ["day", "site", "det"])

    outf = open(fname, "w")
    outf.write("day,site,det,gain\n")

    for row in data:
        outf.write("%d,%d,%d,%f\n" %
                   (row["day"], row["site"], row["det"], row["gain"]))


if __name__ == '__main__':
    dump()
