using FiniteDifferences: central_fdm
using Plots
using Printf
using Roots: fzero
using StatsBase
using Statistics
using ThreadTools
using QuadGK

pyplot()

# Formulas from Vogel-Beacom 1999

# From PDG 2011 unless otherwise noted.
ħ = 6.58211899e-22              # MeV s
ħc = 197.3269631                # MeV fm
me = 0.51099891                 # MeV
Mn = 939.565345                 # MeV
Mp = 938.272013                 # MeV
GF = 1.16637e-11                # MeV-2 ħc3
fV = 1                          # Vogel-Beacom "f"
gA = 1.2701                     # Vogel-Beacom "g"
# f2 should be 4.70589???
f2 = 3.70589                    # μ_p - μ_n (in units of nuclear magneton)
cosθc = 0.974
ΔR = 0.024  # Hardy and Towner, AIP Conf. Proc. 481, 129 (1999), 10.1063/1.59543
# The remaining constants are only used in σtot0_alt
fR = 1.7152                     # Phase space factor, Vogel-Beacom
τn = 881.5 / ħ                  # Neutron mass, MeV

M = (Mn + Mp) /2
Δ = Mn - Mp
y = √((Δ^2 - me^2)/2)

fm2cm = 1e-13
σ0 = fm2cm^2 * 1/π * ħc^2 * GF^2 * cosθc^2 * (1 + ΔR)


function kinematics(cosθ, Eν)
    p(E) = √(E^2 - me^2)
    v(E) = p(E) / E

    Ee0 = Eν - Δ
    pe0 = p(Ee0)
    ve0 = v(Ee0)

    Ee1 = Ee0 * (1 - Eν/M * (1 - ve0*cosθ)) - y^2/M
    pe1 = p(Ee1)
    ve1 = v(Ee1)

    return Ee0, pe0, ve0, Ee1, pe1, ve1
end

function Ee1(cosθ, Eν)
    return kinematics(cosθ, Eν)[4]
end

function dσ_dcosθ(cosθ, Eν)
    Ee0, pe0, ve0, Ee1, pe1, ve1 = kinematics(cosθ, Eν)

    Γ = (2gA*(fV + f2)*((2Ee0 + Δ)*(1 - ve0*cosθ) - me^2/Ee0)
         + (fV^2 + gA^2)*(Δ*(1 + ve0*cosθ) + me^2/Ee0)
         + (fV^2 + 3gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)
         + (fV^2 - gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)*ve0*cosθ)

    return (σ0/2*((fV^2 + 3gA^2) + (fV^2 - gA^2)ve1*cosθ)Ee1*pe1
            - σ0/2*(Γ/M)*Ee0*pe0)
end

function dσ_dEe(Ee, Eν)
    cosθ = fzero(cθ -> Ee1(cθ, Eν) - Ee, 0)
    dE_dcosθ = central_fdm(5, 1).(cθ -> Ee1(cθ, Eν), cosθ)
    return dσ_dcosθ(cosθ, Eν) / dE_dcosθ
end

# dP / dE = dP / dcosθ * dcosθ / dE

function σ_tot(Eν)
    if Eν == 1.8
        return 0.0
    end
    quadgk(cθ -> dσ_dcosθ(cθ, Eν), -1, 1, rtol=1e-7)[1]
end

function σ_tot0(Eν)
    Ee0 = Eν - Δ
    pe0 = √(Ee0^2 - me^2)
    σ0 * (fV^2 + 3gA^2) * Ee0 * pe0
end

function σ_tot0_alt(Eν)
    Ee0 = Eν - Δ
    pe0 = √(Ee0^2 - me^2)
    fm2cm^2 * ħc^2 * (2π^2 / me^5) / (fR * τn) * Ee0 * pe0
end

# cosθspace() = range(-1, 1, length=1001)
cosθspace() = range(-1, 1, length=101) |> collect

function Espace(Eν; length=101)
    Emin, Emax = Ee1(-1, Eν), Ee1(1, Eν)
    return range(Emin, Emax, length=length) |> collect
end

function pdf(xs, ys)
    dx = xs[2] - xs[1]
    return xs, ys / sum(ys) / dx
end

function pdf_cosθ(Eν)
    cosθ = cosθspace()
    dσ = dσ_dcosθ.(cosθ, Eν)
    return pdf(cosθ, dσ)
end

function pdf_Ee1_old(Eν)
    cosθ = cosθspace()
    dE_dcosθ = central_fdm(5, 1).(cθ -> Ee1(cθ, Eν), cosθ)
    E = Ee1.(cosθ, Eν)
    return pdf(E, dσ_dcosθ.(cosθ, Eν) ./ dE_dcosθ)
end

function pdf_Ee1(Eν, Ee=nothing)
    if isnothing(Ee)
        Ee = Espace(Eν)
    end
    dσ = dσ_dEe.(Ee, Eν)
    return pdf(Ee, dσ)
end

# function pdf_Ee1_diff(Eν)
#     E, P = pdf_Ee1(Eν)
#     return E .- Eν, P
# end

function pdf_Ee1_pctDiff_relToMean(Eν)
    E, P = pdf_Ee1(Eν)
    Emean = mean(E, weights(P))
    ErelPct = 100 * (E .- Emean) / Emean
    return pdf(ErelPct, P)
end

function histmean(centers, vals)
    return mean(centers, weights(vals))
end

function histstd(centers, vals)
    return std(centers, weights(vals))
end

function labels(rEν)
    l = ["\$E_ν\$ = $(@sprintf("%.0f", Eν)) MeV" for Eν in rEν]
    return permutedims(l)
end

function plot_pdf_cosθ()
    rEν = range(2., 9., step=1.)
    xss, yss = collect.(zip(pdf_cosθ.(rEν)...))
    frob!(xss, yss)
    plot(xss, yss, labels=labels(rEν),
         title="PDF of positron angle",
         xlabel="cos θ",
         ylabel="Prob. / cos θ")
end

function plot_pdf_Ee1_diff()
    rEν = range(2., 8., step=1.)
    xss, yss = collect.(zip(pdf_Ee1_diff.(rEν)...))
    plot(xss, yss, labels=labels(rEν),
         title="PDF of positron energy minus antineutrino energy",
         xlabel="\$E_e - E_\\nu\$ [MeV]")
end

function plot_Ee1_diff_vs_cosθ()
    rEν = range(2., 9., step=1.)
    cosθ = cosθspace()
    Es = [Eν .- Ee1.(cosθ, Eν) for Eν in rEν]
    plot(cosθ, Es, labels=labels(rEν),
         title="Antineutrino energy minus positron energy vs cos θ",
         xlabel="cos θ",
         ylabel="\$E_\\nu - E_e\$ [MeV]")
end

function frob!(xss, yss)
    ϵ = eps(xss[1][1])
    for (xs, ys) in zip(xss, yss)
        pushfirst!(xs, xs[1] - ϵ)
        push!(xs, xs[end] + ϵ)
        pushfirst!(ys, 0)
        push!(ys, 0)
    end
end

function plot_pdf_Ee1_pctDiff_relToMean()
    rEν = range(2., 9., step=1.)
    xss, yss = zip(pdf_Ee1_pctDiff_relToMean.(rEν)...) .|> collect
    frob!(xss, yss)
    plot(xss, yss, labels=labels(rEν),
         title="PDF of positron energy relative to mean",
         xlabel="\$(E_e-\\overline{E_e})/\\overline{E_e}\$ [%]",
         ylabel="Prob. / 1%")
end

function Estd_pct(Eν)
    Ee = Espace(Eν, length=500)
    _Ee, P = pdf_Ee1(Eν, Ee)
    Emean = mean(Ee, weights(P))
    Estd = std(Ee, weights(P))
    return 100 * Estd / Emean
end

# function Estd_pct2(Eν)
#     Ee = Espace(Eν, length=1000)
#     _Ee, P = pdf_Ee1(Eν, Ee)
#     Emean = mean(Ee, weights(P))
#     Estdev = stdev(Ee, weights(P))
#     return 100 * Estdev / Emean
# end

function plot_Estd_pct()
    xs = range(2., 9., step=0.05)
    ys = tmap(Estd_pct, xs)
    plot(xs, ys, labels=nothing,
         title="Positron energy spread vs antineutrino energy",
         xlabel="\$ E_\\nu \$ [MeV]",
         ylabel="\$\\sigma(E_e) / \\overline{E_e}\$ [%]")
end
