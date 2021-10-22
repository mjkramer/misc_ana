# Formulas from Vogel-Beacom 1999

# This closely replicates Wei's results
module IbdXsec2011WrongF2
export dσ_dcosθ_2011_wrongF2, σ_tot_2011_wrongF2

using QuadGK

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

function dσ_dcosθ_2011_wrongF2(cosθ, Eν)
    Ee0, pe0, ve0, Ee1, pe1, ve1 = kinematics(cosθ, Eν)

    Γ = (2gA*(fV + f2)*((2Ee0 + Δ)*(1 - ve0*cosθ) - me^2/Ee0)
         + (fV^2 + gA^2)*(Δ*(1 + ve0*cosθ) + me^2/Ee0)
         + (fV^2 + 3gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)
         + (fV^2 - gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)*ve0*cosθ)

    return (σ0/2*((fV^2 + 3gA^2) + (fV^2 - gA^2)ve1*cosθ)Ee1*pe1
            - σ0/2*(Γ/M)*Ee0*pe0)
end

σ_tot_2011_wrongF2(Eν) = quadgk(cθ -> dσ_dcosθ_2011_wrongF2(cθ, Eν),
                                -1, 1, rtol=1e-7)[1]

end


module IbdXsec2011
export dσ_dcosθ_2011, σ_tot_2011

using QuadGK

# From PDG 2011 unless otherwise noted.
ħ = 6.58211899e-22              # MeV s
ħc = 197.3269631                # MeV fm
me = 0.51099891                 # MeV
Mn = 939.565345                 # MeV
Mp = 938.272013                 # MeV
GF = 1.16637e-11                # MeV-2 ħc3
fV = 1                          # Vogel-Beacom "f"
gA = 1.2701                     # Vogel-Beacom "g"
f2 = 4.70589                    # μ_p - μ_n (in units of nuclear magneton)
cosθc = 0.974
ΔR = 0.024  # Hardy and Towner, AIP Conf. Proc. 481, 129 (1999), 10.1063/1.59543

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

function dσ_dcosθ_2011(cosθ, Eν)
    Ee0, pe0, ve0, Ee1, pe1, ve1 = kinematics(cosθ, Eν)

    Γ = (2gA*(fV + f2)*((2Ee0 + Δ)*(1 - ve0*cosθ) - me^2/Ee0)
         + (fV^2 + gA^2)*(Δ*(1 + ve0*cosθ) + me^2/Ee0)
         + (fV^2 + 3gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)
         + (fV^2 - gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)*ve0*cosθ)

    return (σ0/2*((fV^2 + 3gA^2) + (fV^2 - gA^2)ve1*cosθ)Ee1*pe1
            - σ0/2*(Γ/M)*Ee0*pe0)
end

σ_tot_2011(Eν) = quadgk(cθ -> dσ_dcosθ_2011(cθ, Eν),
                        -1, 1, rtol=1e-7)[1]

end


module IbdXsec2021WrongF2
export dσ_dcosθ_2021_wrongF2, σ_tot_2021_wrongF2

using QuadGK

# From PDG 2021 except ΔR
ħc = 197.326_980_4                # MeV fm
me = 0.510_998_950                # MeV
Mn = 939.565_420_52               # MeV
Mp = 938.272_088_16               # MeV
GF = 1.166_378_7e-11              # MeV-2  ħc3
fV = 1                            # Vogel-Beacom "f"
gA = 1.2754                       # Vogel-Beacom "g"
f2 = 3.7058900446               # mu_p - mu_n in units of nuclear magneton
cosθc = 0.974011
ΔR = 0.024  # Hardy and Towner, AIP Conf. Proc. 481, 129 (1999), 10.1063/1.59543

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

function dσ_dcosθ_2021_wrongF2(cosθ, Eν)
    Ee0, pe0, ve0, Ee1, pe1, ve1 = kinematics(cosθ, Eν)

    Γ = (2gA*(fV + f2)*((2Ee0 + Δ)*(1 - ve0*cosθ) - me^2/Ee0)
         + (fV^2 + gA^2)*(Δ*(1 + ve0*cosθ) + me^2/Ee0)
         + (fV^2 + 3gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)
         + (fV^2 - gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)*ve0*cosθ)

    return (σ0/2*((fV^2 + 3gA^2) + (fV^2 - gA^2)ve1*cosθ)Ee1*pe1
            - σ0/2*(Γ/M)*Ee0*pe0)
end

σ_tot_2021_wrongF2(Eν) = quadgk(cθ -> dσ_dcosθ_2021_wrongF2(cθ, Eν),
                                -1, 1, rtol=1e-7)[1]

end


module IbdXsec2021
export dσ_dcosθ_2021, σ_tot_2021

using QuadGK

# From PDG 2021 except ΔR
ħc = 197.326_980_4                # MeV fm
me = 0.510_998_950                # MeV
Mn = 939.565_420_52               # MeV
Mp = 938.272_088_16               # MeV
GF = 1.166_378_7e-11              # MeV-2  ħc3
fV = 1                            # Vogel-Beacom "f"
gA = 1.2754                       # Vogel-Beacom "g"
f2 = 4.7058900446               # mu_p - mu_n in units of nuclear magneton
cosθc = 0.974011
ΔR = 0.024  # Hardy and Towner, AIP Conf. Proc. 481, 129 (1999), 10.1063/1.59543

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

function dσ_dcosθ_2021(cosθ, Eν)
    Ee0, pe0, ve0, Ee1, pe1, ve1 = kinematics(cosθ, Eν)

    Γ = (2gA*(fV + f2)*((2Ee0 + Δ)*(1 - ve0*cosθ) - me^2/Ee0)
         + (fV^2 + gA^2)*(Δ*(1 + ve0*cosθ) + me^2/Ee0)
         + (fV^2 + 3gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)
         + (fV^2 - gA^2)*((Ee0 + Δ)*(1 - cosθ/ve0) - Δ)*ve0*cosθ)

    return (σ0/2*((fV^2 + 3gA^2) + (fV^2 - gA^2)ve1*cosθ)Ee1*pe1
            - σ0/2*(Γ/M)*Ee0*pe0)
end

σ_tot_2021(Eν) = quadgk(cθ -> dσ_dcosθ_2021(cθ, Eν),
                        -1, 1, rtol=1e-7)[1]

end
