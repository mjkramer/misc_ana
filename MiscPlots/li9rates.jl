# Prompt energy cut: [3.5, 6, 8] MeV
effs = [0.783, 0.43, 0.168]
effs_syst = [0.054, 0.029, 0.014]

# from new_li9_rates.txt (3e5 pe)
rates = Dict([1 => [164.0, 554.9, 6969.2],
              2 => [95.8, 301.7, 6282.7],
              3 => [66.8, 280.1, 1915.1]])

# from new_li9_rates.txt (3e5 pe)
# except mid-range, which is from matt_li9_rates.txt (3.2e5 pe)
uncs = Dict([1 => [51.4, 200.5, 675.4],
             2 => [27.4, 118.5, 733.3],
             3 => [25.5, 89.4, 182.4]])

eff_veto = [0.8711, 0.9015, 0.9883]
eff_mult = [0.9772, 0.9782, 0.9829]
livetime = [1737, 1729, 1737]
ndet = [1.8888, 1.8925, 3.8921]
t_shower = 400.4
t_li9 = 257.2
t_he8 = 171.6
frac_he8 = 0.055

# ranges is a list of ints \in {1, 2, 3}, corresponding to PE ranges
# returns the fraction of the final 9Li rate coming from the given ranges
function frac_old(hall, ranges)
    showerSurvProb = 0.21
    r_raw = rates[hall]
    eff_low = (hall == 3) ? effs[2] : effs[3]
    eff_high = effs[1]

    r = [r_raw[1] / eff_low, r_raw[2] / eff_low, r_raw[3] / eff_high * showerSurvProb]

    return sum(r[ranges]) / sum(r)
end

function weights(hall, arr=rates)
    showerSurvProb = (1 - frac_he8) * exp(-t_shower / t_li9) + frac_he8 * exp(-t_shower / t_he8)
    eff_n = 1
    Nlow, Nmid, Nhigh = arr[hall]

    eff_low = (hall == 3) ? effs[2] : effs[3]
    eff_mid = eff_low
    eff_high = effs[1]

    wt_low = Nlow / eff_low / eff_n
    wt_mid = Nmid / eff_mid
    wt_high = Nhigh / eff_high * showerSurvProb

    return wt_low, wt_mid, wt_high
end

function frac(hall, ranges)
    wts = weights(hall)
    return sum(wts[ranges]) / sum(wts)
end

function net_prompt_unc(hall)
    syst_low = (hall == 3) ? effs_syst[2] : effs_syst[3]
    syst_mid = syst_low
    syst_high = effs_syst[1]

    unc_low = sqrt(syst_low^2 + 0.01^2)
    unc_mid = sqrt(syst_mid^2 + 0.01^2)
    unc_high = sqrt(syst_high^2 + 0.01^2)

    wt_low, wt_mid, wt_high = weights(hall)
    sum_wt = wt_low + wt_mid + wt_high

    return (wt_low * unc_low + wt_mid * unc_mid + wt_high * unc_high) / sum_wt
end

function net_ntag_unc(hall)
    wt_low, wt_mid, wt_high = weights(hall)
    return wt_low * 0.45 / (wt_low + wt_mid + wt_high)
end

function final(hall, arr)
    coef = 1 / (eff_veto[hall] * eff_mult[hall] * livetime[hall] * ndet[hall])
    return coef * sum(weights(hall, arr))
end

function final_rate(hall)
    return final(hall, rates)
end

function final_stat_unc(hall)
    return final(hall, uncs) / final(hall, rates)
end

function total_unc(hall)
    stat = final_stat_unc(hall)
    spec = 0.05
    prompt = net_prompt_unc(hall)
    ntag_eff = net_ntag_unc(hall)
    ntag_cut = 0.10
    binning = 0.05
    he8_fit = 0.10
    he8_surv = 0.02

    vals = [stat, spec, prompt, ntag_eff,
            ntag_cut, binning, he8_fit, he8_surv]

    return sqrt(sum(vals.^2))
end
