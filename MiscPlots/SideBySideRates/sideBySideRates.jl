include("../dumpBigTable.jl")   # read_theta13
include("oscProb.jl")
include("readers.jl")

using Pipe: @pipe
using StatsBase

inf2zero(a::AbstractArray) = [(isinf(x) ? zero(x) : x) for x in a]
nan2zero(a::AbstractArray) = [(isnan(x) ? zero(x) : x) for x in a]
nan2missing(a::AbstractArray) = [(isnan(x) ? missing : x) for x in a]

function masscorr(det)
    tm = read_theta13(8).target_mass
    return tm[det] / tm[1]
end

function predict_full(det, ndets::Integer)
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

    return masscorr(det) * sum(pred(c) for c in cores)
end

function predict_full(det, ndets::AbstractArray=[6, 8, 7])
    livetimes = [read_theta13(ndet)[det, "livetime"]
                 for ndet in ndets]
    wts = livetimes ./ sum(livetimes)
    rates = [predict_full(det, ndet) for ndet in ndets]
    return sum(rates .* wts)
end

function predict_simple(det)
    bl = read_baselines()
    cores = names(bl)[2:end]

    return masscorr(det) * sum(1/bl[det, core]^2 for core in cores)
end

# predict(a...; kw...) = predict_simple(a...; kw...)

function ibd_rate(det, ndets::AbstractArray=[6, 8, 7])
    t13 = read_theta13.(ndets)
    rates, stats, systs = zip(ibd_rate.(t13, det, corrmass=false)...)

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
    pred_simple = predict_simple.(1:8)
    pred_full = predict_full.(1:8, Ref(ndets))
    # wts = 1 ./ meas_errs.^2 |> nan2zero
    # scales = meas_rates ./ rawpred |> nan2zero
    # scale = mean(scales, weights(wts))
    # pred_rates = scale .* rawpred

    return DataFrame(pred_simple = pred_simple,
                     pred_full = pred_full |> nan2missing,
                     meas_rates = meas_rates |> nan2missing,
                     meas_errs = meas_errs |> nan2missing)
end

function plot_lianghong()
    labels = ["AD1/AD2", "AD3/AD8", "AD4/EH3", "AD5/EH3", "AD6/EH3",
              "AD4/EH3", "AD5/EH3", "AD6/EH3", "AD7/EH3"]

    df68 = sidebyside_data([6, 8])
    df78 = sidebyside_data([7, 8])
    df6 = sidebyside_data([6])

    function getvals(df, plotdets, normdets)
        pred_simple_norm = mean(df.pred_simple[normdets])
        pred_full_norm = mean(df.pred_full[normdets])
        meas_norm = mean(df.meas_rates[normdets])

        pred_simple_ratios = df.pred_simple[plotdets] ./ pred_simple_norm
        pred_full_ratios = df.pred_full[plotdets] ./ pred_full_norm
        meas_ratios = df.meas_rates[plotdets] ./ meas_norm
        meas_ratio_errs = df.meas_errs[plotdets] ./ meas_norm
        return pred_simple_ratios, pred_full_ratios, meas_ratios, meas_ratio_errs
    end

    function build(desc)
        unwrap(l) = cat(l..., dims=1) # flatten array of arrays
        return @pipe (getvals.(myzip(desc)...)) |> myzip |> map(unwrap, _)

        # results = (getvals(args...) for args in desc)
        # pred_wrap, meas_wrap, meas_err_wrap = myzip(results)
        # return map(unwrap, (pred_wrap, meas_wrap, meas_err_wrap))
    end

    ypred_simple, ypred_full, ymeas, ymeas_err =
        build([(df68, [1], [2]),
               (df78, [3], [4]),
               (df6, [5, 6, 7], [5, 6, 7]),
               (df78, [5, 6, 7, 8], [5, 6, 7, 8])
               ])

    xpred_hack = [0.5, eachindex(labels)..., length(labels)+0.5]
    ypred_simple_hack = [ypred_simple[1], ypred_simple..., ypred_simple[end]]
    ypred_full_hack = [ypred_full[1], ypred_full..., ypred_full[end]]
    plot(xpred_hack, ypred_simple_hack, st=:stepmid, ls=:dash, c=:red, label="Exp. (simple)")
    plot!(xpred_hack, ypred_full_hack, st=:stepmid, ls=:dash, c=:blue, label="Exp. (full)")

    scatter!(ymeas, yerror=ymeas_err, xerror=0.5, c=:black, label="Observed")
    vline!([1.5, 2.5, 5.5], ls=:dash, c=:black, label=nothing)
    xticks!(eachindex(labels), labels)
    ylabel!("Ratio of IBD rates")
    title!("P17B IBD rate comparison")
end
