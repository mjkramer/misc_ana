const SINSQ_2T12 = 0.8510             # PDG 2018
const SINSQ_2T13 = 0.0856             # P17B paper

# In eV^2:
const DM21 = 7.53e-5                  # PDG 2018
const DMee = 2.522e-3                 # P17B paper

to_angle(x) = asin(sqrt(x)) / 2
const TH12 = to_angle(SINSQ_2T12)
const TH13 = to_angle(SINSQ_2T13)

# Here "LE" (L/E) is in m/MeV

function th12_term(LE)
    D21 = 1.267 * DM21 * LE
    return cos(TH13)^4 * sin(2*TH12)^2 * sin(D21)^2
end

function th13_term(LE)
    Dee = 1.267 * DMee * LE
    return sin(2*TH13)^2 * sin(Dee)^2
end

function surv_prob(LE)
    return 1 - th12_term(LE) - th13_term(LE)
end
