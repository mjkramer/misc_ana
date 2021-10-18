include("../dumpBigTable.jl")   # read_theta13
include("oscProb.jl")
include("readers.jl")

using StatsBase

function predict(det, ndets::Integer)
    t13 = read_theta13(ndets)
    livetime = t13[1, "livetime"] # days

    spec = read_reac_spec(ndets)
    xsec = read_xsec()
    df = innerjoin(spec, xsec, on="Enu")

    bl = read_baselines()
    cores = names(bl)[2:end]

    function pred(core)
        L = bl[det, core]
        predspec = @. df[:, core] * df.xsec * surv_prob(L/df.Enu) / L^2
        return sum(predspec)
    end

    return sum(pred(c) for c in cores)
end

function predict(det, ndets::AbstractArray=[6, 8, 7])
    livetimes = [read_theta13(ndet)[det, "livetime"]
                 for ndet in ndets]
    wts = livetimes ./ sum(livetimes)
    rates = [predict(det, ndet) for ndet in ndets]
    return sum(rates .* wts)
end

function ibd_rate(det, ndets::AbstractArray=[6, 8, 7])
    t13 = read_theta13.(ndets)
    rates, stats, systs = zip(ibd_rate.(t13, det)...)

    livetimes = [t[det, "livetime"] for t in t13]
    wts = livetimes ./ sum(livetimes)

    rate = sum(rates .* wts)
    stat = (stats .* wts).^2 |> sum |> sqrt
    syst = systs .* wts |> sum
    err = sqrt(stat^2 + syst^2)
    return rate, err
end
