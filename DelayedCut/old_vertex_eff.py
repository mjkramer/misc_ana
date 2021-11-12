from functools import lru_cache

import uproot


# NOTE: This is no longer used. Vertex eff now done in IbdSel's fit_prep.


PBP_DIR = '/global/cfs/cdirs/dayabay/scratch/mkramer/thesis_data/p17b' + \
    '/stage2_pbp/2021_02_03@yolo5'


def nADs_for(site, det):
    if (site, det) == (1, 1):
        return [6, 8]
    elif (site, det) in [(2, 2), (3, 4)]:
        return [8, 7]
    else:
        return [6, 8, 7]


def det_active(nADs, site, det):
    if nADs == 6:
        return ((site == 1 and det in [1, 2]) or
                (site == 2 and det in [1]) or
                (site == 3 and det in [1, 2, 3]))
    if nADs == 8:
        return ((site == 1 and det in [1, 2]) or
                (site == 2 and det in [1, 2]) or
                (site == 3 and det in [1, 2, 3, 4]))
    if nADs == 7:
        return ((site == 1 and det in [2]) or
                (site == 2 and det in [1, 2]) or
                (site == 3 and det in [1, 2, 3, 4]))
    raise


def dets_for(site):
    if site not in [1, 2, 3]:
        raise
    return [1, 2, 3, 4] if site == 3 else [1, 2]


def idet(site, det):
    return (site-1)*2 + (det-1)


@lru_cache()
def ibd_tree(site, det, nADs=-1):
    nADs = nADs_for(site, det) if nADs == -1 else [nADs]
    files = [f"{PBP_DIR}/stage2.pbp.eh{site}.{n}ad.root:ibd_AD{det}"
             for n in nADs]
    return uproot.concatenate(files, library="pd")


def vertex_eff(site, det, nADs=-1):
    tree = ibd_tree(site, det, nADs)
    n_cut = len(tree.query("zP < 0 and zD < 0"))
    n_tot = len(tree)
    return n_cut / n_tot


def all_vertex_effs(nADs=-1):
    result = []
    for site in [1, 2, 3]:
        for det in [1, 2, 3, 4] if site == 3 else [1, 2]:
            active = nADs == -1 or det_active(nADs, site, det)
            eff = vertex_eff(site, det, nADs) if active else 0
            result.append(eff)
    return result


def fudge_eff(t13file, nADs):
    in_lines = open(t13file).readlines()
    f_out = open(t13file, "w")

    out_lines = []
    line_indices = {}
    headers_remaining = 3

    for line in in_lines:
        out_lines.append(line)

        if line.strip().startswith("#"):
            continue

        if headers_remaining > 0:
            headers_remaining -= 1
            continue

        words = line.strip().split()
        rownum = int(words[1])
        line_indices[rownum] = len(out_lines) - 1

    def get_vals(rownum, typ):
        lineno = line_indices[rownum]
        return [typ(w) for w in
                out_lines[lineno].split()[2:]]

    nom_del_effs = get_vals(5, float)

    def new_vals(func, *args, **kwargs):
        result = []
        for site in [1, 2, 3]:
            for det in dets_for(site):
                if det_active(nADs, site, det):
                    result.append(func(site, det, *args, **kwargs))
                else:
                    result.append(0)
        return result

    def del_eff(site, det):
        i = idet(site, det)
        return vertex_eff(site, det, nADs) * nom_del_effs[i]
    del_effs = new_vals(del_eff)

    def replace_line(rownum, vals, fmt="%f"):
        i = line_indices[rownum]
        part1 = " ".join(out_lines[i].split()[:2])
        part2 = " ".join(fmt % v for v in vals)
        out_lines[i] = f"{part1} {part2}\n"

    replace_line(5, del_effs, "%.4f")

    for line in out_lines:
        f_out.write(line)

    f_out.close()


def fudge_eff_all(direc):
    for nADs in [6, 8, 7]:
        t13file = f"{direc}/Theta13-inputs_P17B_inclusive_{nADs}ad.txt"
        fudge_eff(t13file, nADs)
