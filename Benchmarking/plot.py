#!/usr/bin/env python3

import matplotlib.pyplot as plt

def read():
    results = {}
    current = None

    for line in open('results.txt'):
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith('#'):
            id = line.split()[3]
            nfiles = int(id.split('/')[1])
            current = results.setdefault(nfiles, [])
        else:
            words = line.split()
            ntasks = int(words[0])
            try:
                nodesec = float(words[2])
            except:
                continue
            current.append((ntasks, nodesec))

    return results

def show():
    r = read()
    for nfiles in sorted(r.keys()):
        data = r[nfiles]
        xs, ys = zip(*data)
        # ys = [5676 * y / 3600 * 80 for y in ys]
        ys = [5676 * y / 3600 for y in ys]
        plt.plot(xs, ys, '.', label=f'{nfiles}-day benchmark')
        plt.xlabel('# processes per Xeon Phi "Knight\'s Landing" node')
        # plt.ylabel('MPP hours for P17B')
        plt.ylabel('Node-hours to process P17B')
        plt.legend()
        plt.title('LBNL IBD selection: Performance vs. level of parallelism')
        plt.tight_layout()
        plt.savefig("benchmarking.pdf")

if __name__ == '__main__':
    show()
