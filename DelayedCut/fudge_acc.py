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


def fudge_acc(t13file, nADs, fudge_pct):
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

    nom_acc_rates = get_vals(11, float)
    nom_acc_errs = get_vals(12, float)

    def new_vals(func):
        result = []
        for site in [1, 2, 3]:
            for det in dets_for(site):
                if det_active(nADs, site, det):
                    result.append(func(site, det))
                else:
                    result.append(0)
        return result

    scale = 1. + 0.01 * fudge_pct

    def acc_rate(site, det):
        i = idet(site, det)
        return scale * nom_acc_rates[i]
    acc_rates = new_vals(acc_rate)

    def acc_err(site, det):
        i = idet(site, det)
        return scale * nom_acc_errs[i]
    acc_errs = new_vals(acc_err)

    def replace_line(rownum, vals, fmt="%f"):
        i = line_indices[rownum]
        part1 = " ".join(out_lines[i].split()[:2])
        part2 = " ".join(fmt % v for v in vals)
        out_lines[i] = f"{part1} {part2}\n"

    replace_line(11, acc_rates, "%.3f")
    replace_line(12, acc_errs, "%.5f")

    for line in out_lines:
        f_out.write(line)

    f_out.close()
