import ROOT as R


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
