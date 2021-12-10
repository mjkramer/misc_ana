using PyCall

py"""
import ROOT as R
R.gROOT.SetBatch(1)
import os
#selhome = os.getenv('IBDSEL_HOME')
selhome = '/home/mkramer/physics/ana4thesis/IbdSel/code'

R.gSystem.Load(f'{selhome}/selector/_build/common.so')
R.gSystem.Load(f'{selhome}/selector/_build/stage2.so')
"""

using Plots
using Polynomials: fit
pyplot()
# plotlyjs()
default(palette=:tab10)

Mode = py"R.Li9Calc.Mode"
ALLMODES = [Mode.Nominal, Mode.NoB12,
            Mode.Fix15pctHe8, Mode.NoHe8]

const MODENAMES = Dict([
    Mode.Nominal => "Nominal",
    Mode.NoB12 => raw"No $^{12}$B",
    Mode.Fix15pctHe8 => raw"15% $^8$He",
    Mode.NoHe8 => raw"No $^8$He"
])

const COLORS = Dict([
    Mode.Nominal => :blue,
    Mode.NoB12 => :orange,
    Mode.Fix15pctHe8 => :green,
    Mode.NoHe8 => :red,
])


function getpoints(site, mode=Mode.Nominal)
    c = py"R.Li9Calc()"
    c.setMode(mode)
    xs = c.MIN_VETO_BDRY_PE:c.DELTA_VETO_BDRY_PE:c.MAX_VETO_BDRY_PE
    # xs = 2e5:c.DELTA_VETO_BDRY_PE:c.MAX_VETO_BDRY_PE
    # xs = 2.5e5:0.1e5:3.5e5
    ys = c.li9daily_nearest.(site, xs, 400.4)
    xs, ys = xs[3:end], ys[3:end]
    points = [(x, y) for (x, y) in zip(xs, ys) if y < 3.5]
    return collect.(zip(points...))
end

function printlinreg(site, mode=Mode.Nominal)
    c = py"R.Li9Calc()"
    c.setMode(mode)
    c.li9daily_linreg(site, 3e5, 400.4)
end

function plotpoints_multi(site, modes=ALLMODES)
    p = plot()
    for mode in modes
        xs, ys = getpoints(site, mode)
        scatter!(xs, ys, label=MODENAMES[mode], color=COLORS[mode])
        if mode == Mode.Nominal
            line = fit(xs, ys, 1)
            print(line)
            printlinreg(site, mode)
            plot!(xs, line.(xs), label=nothing, color=COLORS[mode])
        end
    end
    return p
end

function plotpoints_nominal(site)
    # Note: Could also pass primary=false when plotting the line in order to get
    # the same color.
    p = plot(legend=false, color_palette=[:blue])
    xs, ys = getpoints(site, Mode.Nominal)
    unc = [0.33, 0.32, 0.30][site] # from IbdSel/selector/stage2/Calculator.cc
    scatter!(xs, ys, yerror=unc.*ys)
    line = fit(xs, ys, 1, weights=(unc.*ys).^-2)
    plot!(xs, line.(xs))
    title!("Daily \$^9\$Li/\$^8\$ rate, 400.4 ms veto (EH$site)")
    xlabel!("Shower-muon threshold (PE)")
    ylabel!("Events/AD/day")
    savefig("/home/mkramer/physics/thesis/images/Backgrounds/Li9/linreg/li9_linreg_eh$site.pdf")
    return p
end
