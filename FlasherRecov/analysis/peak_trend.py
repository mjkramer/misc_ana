import ROOT as R

from array import array
from dataclasses import dataclass


R.gStyle.SetOptFit(1)
R.gStyle.SetMarkerStyle(20)
R.gStyle.SetPadLeftMargin(0.15)
R.gStyle.SetPadTopMargin(0.08)


@dataclass
class Peak:
    emin: float
    emax: float
    name: str


@dataclass
class Config:
    fname: str = "../results_eh1_first10.root"
    hall: int = 1
    det: int = 1
    width: int = 5           # number of time-to-flasher bins to group together
    peak: Peak = None


K40 = Peak(1.4, 1.5, "K40")
Tl208 = Peak(2.6, 2.8, "Tl208")


# `width` is the number of Y (time-to-flasher) bins to group together
def peaks(cfg):
    f = R.TFile(cfg.fname)
    h = f.Get("h2_postFlasher_AD%d" % cfg.det)

    xs, ys, yerr = [], [], []

    for leftbin in range(1, h.GetNbinsY()+1, cfg.width):
        rightbin = leftbin + cfg.width - 1
        center = 0.5 * (h.GetYaxis().GetBinLowEdge(leftbin) +
                        h.GetYaxis().GetBinUpEdge(rightbin))
        px = h.ProjectionX("px", leftbin, rightbin, "e")
        res_ = px.Fit("gaus", "0SQ", "goff", cfg.peak.emin, cfg.peak.emax)
        res = res_.Get()

        xs.append(center)
        ys.append(res.GetParams()[1])
        yerr.append(res.GetErrors()[1])

    return xs, ys, yerr


def graph(cfg):
    xs, ys, yerr = peaks(cfg)
    xerr = [cfg.width/2] * len(xs)
    def A(l): return array('d', l)
    g = R.TGraphErrors(len(xs), A(xs), A(ys), A(xerr), A(yerr))
    g.SetTitle(f"%s peak vs time to last flasher, EH%d-AD%d" %
               (cfg.peak.name, cfg.hall, cfg.det))
    g.GetXaxis().SetTitle("Time to last flasher [ms]")
    g.GetYaxis().SetTitle("Peak [MeV]")
    R.SetOwnership(g, False)
    return g


def savepad(pad, cfg=None, _cfgs={}):
    if cfg is None:
        cfg = _cfgs[pad.GetName()]
    imgbase = f"gfx/{cfg.peak.name}_eh1_ad{cfg.det}"
    for ext in ["png", "pdf"]:
        pad.SaveAs(f"{imgbase}.{ext}")
    _cfgs[pad.GetName()] = cfg


def linefit(cfg):
    R.SetOwnership(R.TCanvas(), False)
    g = graph(cfg)
    g.Draw("AP")
    g.Fit("pol1")

    savepad(R.gPad, cfg)


def go():
    for peak in [K40, Tl208]:
        for det in [1, 2]:
            cfg = Config(peak=peak, det=det)
            linefit(cfg)
