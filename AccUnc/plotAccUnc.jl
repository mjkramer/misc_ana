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

@. gaus(x, p) = p[1] * exp(-(x-p[2])^2 / (2*p[3]^2))

@memoize Dict function getsamples(site, det, nADs_list=[6, 8, 7])
    mc = RMC.loadAccUncMC(SELNAME, site, det, "stage2_pbp", nADs_list)

    return [mc.randAccDaily() for _ in 1:NSAMPLES]
end

# See also Plots._make_hist

makehist(samples) = fit(Histogram, samples, nbins=NBINS)

centers(h::Histogram) = (h.edges[1][1:(end-1)] + h.edges[1][2:end]) / 2
binwidth(h::Histogram) = h.edges[1][2] - h.edges[1][1]

function LsqFit.curve_fit(model, h::Histogram, p0)
    return curve_fit(model, centers(h), h.weights, p0)
end

function sample_pct_unc(site, det; kw...)
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
    p, _h = do_fit(site, det; kw...)
    return 100p[3]/p[2]
end

function plothist(site, det; kw...)
    p, h = do_fit(site, det)
    plot(h.edges[1], h.weights, st=:stepbins, legend=false, color=:black)
    xs = centers(h)
    plot!(xs, gaus(xs, p), color=:blue)

    pct_sample = sample_pct_unc(site, det)
    pct_fit = fit_pct_unc(site, det)
    txt = @sprintf "Sample σ = %.3f%%\nFit σ = %.3f%%" pct_sample pct_fit
    xmax = current().subplots[1][:xaxis][:extrema].emax
    ymax = current().subplots[1][:yaxis][:extrema].emax
    annotate!(xmax, ymax, text(txt, :top, :right, pointsize=10))

    title!("Acc. rates after stat. fluctuations, EH$site-AD$det, N=$NSAMPLES")
    xlabel!("Accidentals / day")
    ylabel!(@sprintf "Count / (%.3f / day)" binwidth(h))
end
