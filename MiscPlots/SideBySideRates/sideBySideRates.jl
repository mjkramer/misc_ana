include("oscProb.jl")
include("readers.jl")

using Pipe: @pipe
using Plots
using StatsBase

pyplot(size = (700, 400), grid = false,
       framestyle = :box)

# DATASETS =
#     Dict("P17B" => "2021_02_03@delcut_third_6.000MeV@bcw",
#          "All data" => "2021_02_03+v5v3v1@nominal@bcw",
#          "Post-P17B" => "post17_v5v3v1@nominal@bcw")
DATASETS =
    Dict("Alpha + nGd, P17B" => "p17b_v4_NL@test_newNonUni_alphas_ngd@bcw",
         "Alphas only, P17B" =>  "p17b_v4_NL@test_newNonUni_alphas_only@bcw",
         "No corr., P17B" =>  "p17b_v4_NL@test_newNonUni_off@bcw",
         "Alpha + nGd, Post17" => "post17_v5v3v1_NL@test_newNonUni_alphas_ngd@bcw",
         "Alphas only, Post17" =>  "post17_v5v3v1_NL@test_newNonUni_alphas_only@bcw",
         "No corr., Post17" =>  "post17_v5v3v1_NL@test_newNonUni_off@bcw")

inf2zero(a::AbstractArray) = [(isinf(x) ? zero(x) : x) for x in a]
nan2zero(a::AbstractArray) = [(isnan(x) ? zero(x) : x) for x in a]
nan2missing(a::AbstractArray) = [(isnan(x) ? missing : x) for x in a]

function predict_simple(det)
    bl = read_baselines()
    cores = names(bl)[2:end]

    return masscorr(det) * sum(1/bl[det, core]^2 for core in cores)
end

function masscorr(det)
    tagconfig = first(DATASETS)[2] # all datasets have the same target masses
    tm = read_theta13(7, tagconfig).target_mass
    return tm[det] / tm[1]
end

function predict_full(det, ndet::Integer)
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

    return masscorr(det) * sum(pred(c) for c in cores)
end

function predict_full(det, ndets::AbstractArray, tagconfig)
    livetimes = [read_theta13(ndet, tagconfig)[det, "livetime"]
                 for ndet in ndets]
    wts = livetimes ./ sum(livetimes)
    rates = [predict_full(det, ndet) for ndet in ndets]
    return sum(rates .* wts)
end

function ibd_rate(det, ndets::AbstractArray, tagconfig)
    t13 = read_theta13.(ndets, tagconfig)
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

function sidebyside_data(ndets::AbstractArray, tagconfig)
    meas_rates, meas_errs =
        ibd_rate.(1:8, Ref(ndets), tagconfig) |> myzip
    pred_simple = predict_simple.(1:8)
    pred_full = predict_full.(1:8, Ref(ndets), tagconfig)
    # wts = 1 ./ meas_errs.^2 |> nan2zero
    # scales = meas_rates ./ rawpred |> nan2zero
    # scale = mean(scales, weights(wts))
    # pred_rates = scale .* rawpred

    return DataFrame(pred_simple = pred_simple,
                     pred_full = pred_full |> nan2missing,
                     meas_rates = meas_rates |> nan2missing,
                     meas_errs = meas_errs |> nan2missing)
end

function plot_ratios(dataset, desc, labels, divs)
    plot(reuse=false)

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

    ypred_simple, ypred_full, ymeas, ymeas_err = build(desc)

    xpred_hack = [0.5, eachindex(labels)..., length(labels)+0.5]
    ypred_simple_hack = [ypred_simple[1], ypred_simple..., ypred_simple[end]]
    ypred_full_hack = [ypred_full[1], ypred_full..., ypred_full[end]]
    plot(xpred_hack, ypred_simple_hack, st=:stepmid, ls=:dash, c=:red, label="Pred. (simple)")
    plot!(xpred_hack, ypred_full_hack, st=:stepmid, ls=:dash, c=:blue, label="Pred. (full)")

    scatter!(ymeas, yerror=ymeas_err, xerror=0.5, c=:black, label="Observed")
    vline!(divs, ls=:dash, c=:black, label=nothing)
    xticks!(eachindex(labels), labels)
    ylabel!("Ratio of IBD rates")
    title!("Relative IBD rates ($dataset)")
    savefig("gfx/zoom_post_p17b/$(DATASETS[dataset]).pdf")
    display(current())
end

function plot_ratios_full(dataset)
    labels = ["AD1/AD2", "AD3/AD8", "AD4/EH3", "AD5/EH3", "AD6/EH3",
              "AD4/EH3", "AD5/EH3", "AD6/EH3", "AD7/EH3"]

    df68, df78, df6 = sidebyside_data.([[6, 8], [7, 8], [6]],
                                       DATASETS[dataset])

    desc = [(df68, [1], [2]),
            (df78, [3], [4]),
            (df6, [5, 6, 7], [5, 6, 7]),
            (df78, [5, 6, 7, 8], [5, 6, 7, 8])]

    divs = [1.5, 2.5, 5.5]

    plot_ratios(dataset, desc, labels, divs)
end

function plot_ratios_zoom(dataset)
    labels = ["AD3/AD8", "AD4/EH3", "AD5/EH3", "AD6/EH3", "AD7/EH3"]

    df = sidebyside_data([7, 8], DATASETS[dataset])

    desc = [(df, [3], [4]),
            (df, [5, 6, 7, 8], [5, 6, 7, 8])]

    divs = [1.5]

    plot_ratios(dataset, desc, labels, divs)
end

function plot_ratios_zoom_post17(dataset)
    labels = ["AD3/AD8", "AD4/EH3", "AD5/EH3", "AD6/EH3", "AD7/EH3"]

    df = sidebyside_data([7], DATASETS[dataset])

    desc = [(df, [3], [4]),
            (df, [5, 6, 7, 8], [5, 6, 7, 8])]

    divs = [1.5]

    plot_ratios(dataset, desc, labels, divs)
end

function plot_all_ratios()
    plot_ratios_full("P17B")
    plot_ratios_zoom("All data")
    plot_ratios_zoom("Post-P17B")
    plot_ratios_zoom("P17B")
end

function plot_all_ratios_newNonUni()
    pre_sets = [k for k in keys(DATASETS) if findfirst("P17B", k) !== nothing]
    post_sets = [k for k in keys(DATASETS) if findfirst("Post17", k) !== nothing]
    plot_ratios_full.(pre_sets)
    plot_ratios_zoom.(post_sets)
end
