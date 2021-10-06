using Plots

pyplot()

function σE_rel(Erec)
    a, b, c = 0.016, 0.081, 0.026
    return sqrt(a^2 + (b^2 / Erec) + (c^2 / Erec^2))
end

function plot_σE_rel()
    Erecs = 0.7:0.01:12
    σs = σE_rel.(Erecs) .* 100
    plot(Erecs, σs, color=:black, label="Nominal")

    plot!(Erecs, σs .+ 0.2, color=:blue, label="\$\\pm1\\sigma\$ (corr)")
    plot!(Erecs, σs .- 0.2, color=:blue, label=nothing)

    plot!(Erecs, σs .+ √2*0.2, color=:purple, label="\$\\pm1\\sigma\$ (corr) \$\\pm1\\sigma\$ (uncorr)")
    plot!(Erecs, σs .- √2*0.2, color=:purple, label=nothing)

    title!("Energy resolution")
    xlabel!("Reconstructed energy [MeV]")
    ylabel!("\$\\sigma(E)/E\$")
end
