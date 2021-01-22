def read_ibdsel_config(fname):
    results = {}
    for line in open(fname):
        if line.strip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        key, valstr = parts[:2]
        try:
            val = int(valstr)
        except ValueError:
            try:
                val = float(valstr)
            except ValueError:
                val = valstr
        results[key] = val
    return results
