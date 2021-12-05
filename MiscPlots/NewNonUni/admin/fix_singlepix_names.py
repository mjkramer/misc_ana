#!/usr/bin/env python3

from os.path import isfile
from shutil import copy

from common import CONFIGS
import MyROOT as R


def fix_name(name: str) -> str:
    parts = name.split('_')
    for i in [4, 6]:
        parts[i] = str(int(parts[i]) + 1)
    return '_'.join(parts)


def fix_names(sel: str, site: int):
    direc = f'input/{sel}'
    fname = f'stage2.pbp.eh{site}.7ad.root'
    path = f'{direc}/{fname}'
    origpath = f'{direc}/orig.{fname}'

    if not isfile(origpath):
        copy(path, origpath)

    src = R.TFile(origpath)
    dest = R.TFile(path, "RECREATE")

    for key in src.GetListOfKeys():
        name = key.GetName()
        if name.startswith('h_single') and name.find('r2') != -1:
            newname = fix_name(name)
        else:
            newname = name
        obj = src.Get(name)
        dest.cd()
        if type(obj) is R.TTree:
            obj = obj.CloneTree(-1, 'fast')
        obj.Write(newname)

    dest.Close()
    src.Close()


def main():
    for config in CONFIGS:
        sel = f'post17_v5v3v1_NL@{config}'
        for site in [1, 2, 3]:
            fix_names(sel, site)


if __name__ == '__main__':
    main()
