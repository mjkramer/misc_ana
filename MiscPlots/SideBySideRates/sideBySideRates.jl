include("../dumpBigTable.jl")   # read_theta13
include("oscProb.jl")
include("readers.jl")

using Pipe: @pipe
using StatsBase

inf2zero(a::AbstractArray) = [(isinf(x) ? zero(x) : x) for x in a]
nan2zero(a::AbstractArray) = [(isnan(x) ? zero(x) : x) for x in a]
nan2missing(a::AbstractArray) = [(isnan(x) ? missing : x) for x in a]

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

myzip(a) = @pipe zip(a...) |> map(collect, _)

function sidebyside_data(ndets::AbstractArray=[6, 8, 7])
    meas_rates, meas_errs =
        @pipe ibd_rate.(1:8, Ref(ndets)) |> myzip
    rawpred = predict.(1:8, Ref(ndets))
    wts = 1 ./ meas_errs.^2 |> nan2zero
    scales = meas_rates ./ rawpred |> nan2zero
    scale = mean(scales, weights(wts))
    pred_rates = scale .* rawpred

    return DataFrame(pred_rates = pred_rates |> nan2missing,
                     meas_rates = meas_rates |> nan2missing,
                     meas_errs = meas_errs |> nan2missing)
end
