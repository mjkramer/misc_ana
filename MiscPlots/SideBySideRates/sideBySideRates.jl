include("../dumpBigTable.jl")   # read_theta13
include("oscProb.jl")
include("readers.jl")

function predict(det, ndet::Integer)
    t13 = read_theta13(ndet)
    livetime = t13[1, "livetime"] # days

    spec = read_reac_spec(ndet)
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
    rates = [predict(det, ndet) for ndet in ndets]
    return livetimes .* rates ./ sum(livetimes)
end

function ibd_rate(det, ndets::AbstractArray=[6, 8, 7])
    t13 = read_theta13.(ndets)
    rates, stats, systs = zip(ibd_rate.(t13, det)...)

    livetimes = [t[det, "livetime"] for t in t13]
    tottime = sum(livetimes)
    weights = livetimes ./ tottime

    rate = sum(rates .* weights)
    stat = (stats .* weights).^2 |> sum |> sqrt
    syst = systs .* weights |> sum
    err = sqrt(stat^2 + syst^2)
    return rate, err
end
