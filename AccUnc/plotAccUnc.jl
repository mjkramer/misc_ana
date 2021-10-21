using LsqFit
using Memoization
using Plots
using Printf
using PyCall
using Statistics
using StatsBase

pushfirst!(PyVector(pyimport("sys")["path"]), @__DIR__)
pyplot(grid=false)

SELNAME = "2021_02_03@delcut_third_6.000MeV"
NSAMPLES = 10_000
NBINS = 100

@pyimport runAccUncMC as RMC

@enum Period kAll k6AD=6 k8AD=8 k7AD=7

function nADs_for(period::Period)
    if period == kAll
        return [6, 8, 7]
    end
    return [Int(period)]
end

function name_for(period::Period)
    if period == kAll
        return "all data"
    end
    return "$(Int(period))AD period"
end

function active(period::Period, site, det)
    if period == k6AD
        return !((site, det) in [(2, 2), (3, 4)])
    elseif period == k7AD
        return (site, det) != (1, 1)
    end
    return true
end

@. gaus(x, p) = p[1] * exp(-(x-p[2])^2 / (2*p[3]^2))

@memoize Dict function getsamples(site, det; period=kAll)
    mc = RMC.loadAccUncMC(SELNAME, site, det, "stage2_pbp", nADs_for(period))

    return [mc.randAccDaily() for _ in 1:NSAMPLES]
end

# See also Plots._make_hist

makehist(samples) = fit(Histogram, samples, nbins=NBINS)

centers(h::Histogram) = (h.edges[1][1:(end-1)] + h.edges[1][2:end]) / 2
binwidth(h::Histogram) = h.edges[1][2] - h.edges[1][1]

function LsqFit.curve_fit(model, h::Histogram, p0)
    return curve_fit(model, centers(h), h.weights, p0)
end

macro checkactive(site, det, kw)
    quote
        period = get($(esc(kw)), :period, kAll)
        if !active(period, $(esc(site)), $(esc(det)))
            return missing
        end
    end
end

function sample_pct_unc(site, det; kw...)
    @checkactive(site, det, kw)
    v = getsamples(site, det; kw...)
    μ, σ = mean(v), std(v)
    return 100σ/μ
end

@memoize Dict function do_fit(site, det; kw...)
    v = getsamples(site, det; kw...)
    μ, σ = mean(v), std(v)
    h = makehist(v)
    p0 = [NSAMPLES*binwidth(h)/(σ*√(2π)), μ, σ]
    p = curve_fit(gaus, h, p0) |> coef
    return p, h
end

function fit_pct_unc(site, det; kw...)
    @checkactive(site, det, kw)
    p, _h = do_fit(site, det; kw...)
    return 100p[3]/p[2]
end

function plothist(site, det; kw...)
    p, h = do_fit(site, det; kw...)
    plot(h.edges[1], h.weights, st=:stepbins, legend=false, color=:black)
    xs = centers(h)
    plot!(xs, gaus(xs, p), color=:blue)

    pct_sample = sample_pct_unc(site, det; kw...)
    pct_fit = fit_pct_unc(site, det; kw...)
    txt = @sprintf "Sample σ = %.3f%%\nFit σ = %.3f%%" pct_sample pct_fit
    xmax = current().subplots[1][:xaxis][:extrema].emax
    ymax = current().subplots[1][:yaxis][:extrema].emax
    annotate!(xmax, ymax, text(txt, :top, :right, pointsize=10))

    title!("Acc. rates after stat. fluctuations, EH$site-AD$det, N=$NSAMPLES")
    xlabel!("Accidentals / day")
    ylabel!(@sprintf "Count / (%.3f / day)" binwidth(h))
end

function plotall(period=kAll; kw...)
    ndet(site) = site == 3 ? 4 : 2
    sitedets = [(s, d) for s in [1, 2, 3] for d in 1:ndet(s)]
    sites, dets = zip(sitedets...) .|> collect

    ysamp = sample_pct_unc.(sites, dets; period=period, kw...)
    yfit = fit_pct_unc.(sites, dets; period=period, kw...)

    names = ["EH$s\nAD$d" for (s, d) in sitedets]
    prdname = name_for(period)

    plt = scatter([ysamp yfit], labels=["Sample σ" "Fit σ"], xticks=(1:8, names),
                  xerror=repeat([0.5], 8),
                  markerstrokecolor=:auto,
                  title="Statistical uncertainty of accidentals rate ($prdname)",
                  ylabel="Uncertainty (%)",
                  legend=:topleft,
                  reuse=false)

    savefig("gfx/acc_stat_unc_prd$(Int(period)).pdf")
    return plt
end

function plotallall()
    for period in instances(Period)
        plotall(period)
    end
end
