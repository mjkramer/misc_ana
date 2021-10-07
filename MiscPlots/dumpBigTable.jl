using CSV
using DataFrames

function ibd_rate(df, AD)
    # NB: LBNL analysis does not treat target mass uncertainty

    r = df[AD, :]
    massCorr = df[1, :target_mass] / r.target_mass
    denom = r.livetime * r.veto_eff * r.mult_eff
    k = massCorr / denom

    rate = k*r.obs_evt - r.tot_bkg
    err = sqrt((k^2 * r.obs_evt) + r.tot_bkg_unc^2)
    ndigits = 2
    return rate, err, ndigits
end

const T13_ROWS = Dict([
    1 => :obs_evt,
    2 => :livetime,
    3 => :veto_eff,
    4 => :mult_eff,
    5 => :delcut_eff,
    6 => :power_unc,
    7 => :tot_eff_unc,
    8 => :target_mass,
    9 => :tot_bkg,
    10 => :tot_bkg_unc,
    11 => :acc_bkg,
    12 => :acc_bkg_unc,
    13 => :li9_bkg,
    14 => :li9_bkg_unc,
    15 => :fastn_bkg,
    16 => :fastn_bkg_unc,
    17 => :amc_bkg,
    18 => :amc_bkg_unc,
    19 => :alphan_bkg,
    20 => :alphan_bkg_unc
])

OUT_ROWS = [
    raw"IBD candidates" => :obs_evt,
    raw"Livetime (days)" => :livetime,
    raw"Target mass (kg)" => :target_mass,
    raw"Veto eff." => :veto_eff,
    raw"Mult.\ eff." => :mult_eff,
    raw"Accidentals (day$^{-1}$)" => (:acc_bkg, :acc_bkg_unc),
    raw"$^9$Li/$^8$He (day$^{-1}$)" => (:li9_bkg, :li9_bkg_unc),
    raw"Fast neutrons (day$^{-1}$)" => (:fastn_bkg, :fastn_bkg_unc),
    raw"$^{241}$AmC-$^{13}$C (day$^{-1}$)" => (:amc_bkg, :amc_bkg_unc),
    raw"$^{13}$C($\alpha,n$)-$^{16}$O (day$^{-1}$)" => (:alphan_bkg, :alphan_bkg_unc),
    nothing,
    raw"IBD rate (day$^{-1}$)" => ibd_rate
]

# after the decimal place
NDIGITS = Dict([
    :obs_evt => 0,
    :livetime => 3,
    :target_mass => 0,
    :veto_eff => 4,
    :mult_eff => 4,
])

function ndigits(k)
    if endswith(string(k), "_bkg")
        return 2
    end
    return NDIGITS[k]
end

function read_theta13(path)
    content = ""
    for line in eachline(path, keep=true)
        if strip(line)[1] == '#' || length(split(line)) != 10
            continue
        end
        content *= replace(line, "\t" => " ")
    end
    header = ["period", "varID", repr.(1:8)...]
    df = CSV.read(IOBuffer(content), DataFrame, header=header,
                  delim=" ", ignorerepeated=true)
    select!(df, Not(:period))
    df[!, :varID] = [T13_ROWS[i] for i in df.varID]
    df = permutedims(df, 1, "AD")
    df.AD = [parse(Int, s) for s in df.AD]
    @assert map(rownumber, eachrow(df)) == df.AD
    select!(df, Not(:AD))
    return df
end

# HACK
function fmt(f::Real, nfigs)
    fmtstr = "%.$(nfigs)f"
    return eval(:(@sprintf $fmtstr $f))
end

function fmtrow(cols, name="")
    if name != ""
        name *= " "
    end
    return "  $name&  " * join(cols, " & ") * " \\\\"
end

function getrow(df, spec)
    if isnothing(spec)
        return raw"  \midrule"
    end

    name, src = spec

    function getcell(AD)
        if typeof(src) == Symbol
            val = df[AD, src]
            err = nothing
            n = ndigits(src)
        elseif typeof(src) <: Tuple
            val = df[AD, src[1]]
            err = df[AD, src[2]]
            n = ndigits(src[1])
        elseif typeof(src) <: Function
            val, err, n = src(df, AD)
        end

        if isnothing(err)
            return fmt(val, n)
        else
            return "$(fmt(val, n)) \$\\pm\$ $(fmt(err, n))"
        end
    end

    cells = getcell.(1:8)
    return fmtrow(cells, name)
end

function printrow(args...)
    println(fmtrow(args...))
end

function dump_table(df::DataFrame)
    println(raw"\begin{tabular}{lcccccccc}")
    println(raw"  \toprule")
    hallheads = ["\\multicolumn{$n}{c}{EH$i}"
                 for (i, n) in [(1, 2), (2, 2), (3, 4)]]
    detrheads = ["AD$i" for i in [1, 2, 1, 2, 1, 2, 3, 4]]
    println(fmtrow(hallheads))
    println(fmtrow(detrheads))
    println(raw"  \midrule")

    for spec in OUT_ROWS
        println(getrow(df, spec))
    end

    println(raw"  \bottomrule")
    println(raw"\end{tabular}")
end

function dump_table(path::String)
    read_theta13(path) |> dump_table
end
