def dets_for_period(hall, nADs):
    if nADs == 6:
        return [[1, 2], [1   ], [1, 2, 3   ]][hall-1]
    elif nADs == 8:
        return [[1, 2], [1, 2], [1, 2, 3, 4]][hall-1]
    elif nADs == 7:
        return [[   2], [1, 2], [1, 2, 3, 4]][hall-1]


def dets_for_stage2_file(stage2_path):
    "E.g., '/path/to/stage2.pbp.eh3.6ad.root' => [1, 2, 3]"
    parts = stage2_path.split(".")
    hall = int(parts[-3][2])
    nADs = int(parts[-2][0])
    return dets_for_period(hall, nADs)


def keep(o):
    import ROOT as R
    R.SetOwnership(o, False)     # don't delete it, python!
    try:
        o.SetDirectory(R.gROOT)  # don't delete it, root!
        # o.SetDirectory(0)
    except Exception:
        pass                     # unless you weren't going to anyway
    return o
