#!/usr/bin/env python2.7

from datetime import datetime
import os

SITEDETS = [(1, 1), (1, 2), (2, 1), (2, 2),
            (3, 1), (3, 2), (3, 3), (3, 4)]

DAY0 = datetime(2011, 12, 24)


class DayLister(object):
    def __init__(self):
        self.days = {1: [], 2: [], 3: []}

        fithome = os.environ["LBNL_FIT_HOME"]
        path = fithome + "/ReactorPowerCalculator/dbd_livetime_P17B.txt"

        for line in open(path).readlines():
            day, site, _livetime = line.split()
            self.days[int(site)].append(int(day))

    def days_for(self, site, det):
        daymin, daymax = self._minmax_days(site, det)
        return [day for day in self.days[site]
                if daymin <= day <= daymax]

    def _minmax_days(self, site, det):
        if (site, det) in [(2, 2), (3, 4)]:
            return (218, 2076)
        elif (site, det) == (1, 1):
            return (0, 1824)
        else:
            return (0, 2076)


def dictlistsort(l, keys):
    def compare(x, y):
        for k in keys:
            if x[k] == y[k]:
                continue
            return -1 if x[k] < y[k] else 1
        return 0
    l.sort(cmp=compare)
