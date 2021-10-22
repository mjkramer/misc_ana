include("nuAngDist.jl")         # σ_tot
include("Xsec2021.jl")
using .Xsec2021: σ_tot_2021

using CSV
using DataFrames
using Plots

function compare_σ_to_Wei()
    weifile = ENV["LBNL_FIT_HOME"] * "/toySpectra/reactor/Xsec1_2011.dat"
    df_wei = CSV.read(weifile, DataFrame,
                      delim=" ", ignorerepeated=true, comment="#",
                      header=["Eν", "σ"])
    df_wei = df_wei[2:end, :]      # skip 1.8
    Eν = df_wei.Eν
    σ_wei = df_wei.σ
    σ_ours = σ_tot.(Eν)
    σ_ours0 = σ_tot0.(Eν)
    σ_ours0_alt = σ_tot0_alt.(Eν)

    plot(Eν, [σ_wei σ_ours σ_ours0 σ_ours0_alt],
         labels=["Wei" "Ours 1st" "Ours 0th" "Ours 0th (alt)"],
         legend=:topleft,
         ylim=(0, 1.15e-41), yticks=0:1e-42:1e-41)
end

function compare_2011_to_2021()
    Eν = 1.81:0.01:12
    σ_2011 = σ_tot.(Eν)
    σ_2021 = σ_tot_2021.(Eν)

    plot(Eν, [σ_2011 σ_2021], labels=["PDG 2011" "PDG 2021"],
         legend=:topleft,
         ylim=(0, 1.15e-41), yticks=0:1e-42:1e-41)
end
