#!/usr/bin/env python3
"""HACK: Explicitly list whatever we use from ROOT so that pyright doesn't
complain. Ideally pyright should have the ability to ignore type errors for a
specific module"""

import sys

import ROOT as R

gROOT = R.gROOT
gMinuit = R.gMinuit

TF1 = R.TF1
TH1F = R.TH1F
TTree = R.TTree
TFile = R.TFile
TChain = R.TChain

# powgaus = R.powgaus
# dybf = R.dybf
# mydybf = R.mydbf
# doubcrys = R.doubcrys
# dcbfPlusExp = R.dcbfPlusExp
powgaus = None
dybf = None
mydybf = None
doubcrys = None
dcbfPlusExp = None

# At runtime, replace this with the real ROOT module, so we can access anything
# not explicitly listed above.
sys.modules[__name__] = R
