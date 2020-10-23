import ROOT as R

R.gROOT.ProcessLine(".L ../toymc/muveto_toy.cc+")

def vetoEff(f, det, showerCut, showerTime):
    livetime = f.h_livetime.GetBinContent(1)
    h_wp = f.Get(f"h_wpMuons_ad{det}")
    h_ad = f.Get(f"h_adMuons_ad{det}")

    n_wp = h_wp.Integral(h_wp.FindBin(13), h_wp.GetNbinsX())
    cutbin = h_ad.FindBin(showerCut)
    n_ad = h_ad.Integral(h_ad.FindBin(3000), cutbin - 1)
    n_sh = h_ad.Integral(cutbin, h_ad.GetNbinsX())

    toy = R.MuVetoToy()
    toy.tVetoSh = showerTime
    return toy.vetoEff(n_wp/livetime, n_ad/livetime, n_sh/livetime)

    # t_shVeto = n_sh * showerTime
    # t_adVeto = n_ad * 1_402e-6 * (1 - t_shVeto / livetime)
    # t_wpVeto = n_wp * 602e-6 * (1 - t_shVeto / livetime) * (1 - t_adVeto / livetime)
    # t_adVeto *= (1 - t_wpVeto / livetime)

    # t_shVeto = n_sh * showerTime
    # t_adVeto = n_ad * 1_402e-6
    # t_wpVeto = n_wp * 602e-6
    # t_adVeto *= (1 - t_wpVeto / livetime)

    # return 1 - (t_wpVeto + t_adVeto + t_shVeto) / livetime
