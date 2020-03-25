using Plots
import PyPlot
using Printf

# include("MinTrigSep.jl")

# inspectdr()                     # backend
pyplot()
PyPlot.plt.style.user("dark_background")

df = read_times(f_mine)
dt = timediffs(df, 1)
# histogram(dt)

function loghist()
    bins = 2:0.025:8
    ticks = minimum(bins):0.5:maximum(bins)
    labels = [@sprintf("%.2g", 10^t) for t in ticks]
    # println(labels)
    # xticks = (ticks, labels),

    plot(dt,
         st = :stephist,
         bins = bins,
         xlim = (bins[1], bins[end]),
         normalize = :density,
         xscale = :log10,
         yscale = :log10,
         legend = false,
         title="yo")

end

function dogghist()
    bins = [10^x for x in 2:0.025:8]
    plot(dt,
         st = :stephist,
         bins = bins,
         xlim = (bins[1], bins[end]),
         normalize = :density,
         xscale = :log10,
         yscale = :log10,
         # legend = false,
         # title = "Time difference between triggers",
         xtitle = "nanosec")
end

function plottimes(dt)
    loglim = (2, 8)
    bins = [10^x for x in loglim[1]:0.025:loglim[2]]
    ticks = [10^x for x in loglim[1]:0.5:loglim[2]]
    labels = [@sprintf("%.2g", t) for t in ticks]

    stephist(dt,
             normalize = :density,
             bins = bins,
             xlim = (bins[1], bins[end]),
             xticks = (ticks, labels),
             xscale = :log10,
             yscale = :log10,
             legend = false,
             title = "Time difference between triggers",
             xlabel = "nanosec")
end
