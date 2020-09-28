def vetoEff(tfile, det, showerCut):
    livetime = tfile.livetime.GetVal()
    h_wp = tfile.Get(f"h_wpMuons_ad{det}")
    h_ad = tfile.Get(f"h_adMuons_ad{det}")

    n_wp = h_wp.Integral()
    cutbin = h_ad.FindBin(showerCut)
    n_ad = h_ad.Integral(h_ad.FindBin(3000), cutbin - 1)
    n_sh = h_ad.Integral(cutbin, h_ad.GetNbinsX())

    t_shVeto = n_sh * 400_400e-6
    t_adVeto = n_ad * 1_400e-6 * (1 - t_shVeto / livetime)
    t_wpVeto = n_wp * 600e-6 * (1 - t_shVeto / livetime)

    return 1 - (t_wpVeto + t_adVeto + t_shVeto) / livetime
