using CSV
using DataFrames
using Memoization

function reac_spec_path(ndet)
    dir = "ReactorPowerCalculator/isotope_spectra_by_Beda"
    fname = "reactor_P17B_$(ndet)AD_SNF_nonEq.txt"
    return ENV["LBNL_FIT_HOME"] * "/$dir/$fname"
end

@memoize function read_reac_spec(ndet)
    path = reac_spec_path(ndet)
    return CSV.read(path, DataFrame, delim="\t",
                    header=["Enu", "D1", "D2", "L1", "L2", "L3", "L4"])
end

@memoize function read_xsec()
    path = ENV["LBNL_FIT_HOME"] * "/toySpectra/reactor/Xsec1_2011.dat"
    return CSV.read(path, DataFrame, delim=" ", ignorerepeated=true,
                    comment="#", header=["Enu", "xsec"])
end

@memoize function read_baselines()
    path = ENV["LBNL_FIT_HOME"] * "/toySpectra/unblinded_baseline.txt"
    df = CSV.read(path, DataFrame, delim=" ", ignorerepeated=true)
    rename!(df, "#" => :det)
    # transform!(df, :det => ByRow(s -> parse(Int, s[3])) => :det)
    # df.det = (s -> parse(Int, s[3])).(df.det)
    df.det = [parse(Int, s[3]) for s in df.det]
    sort!(df, :det)
end

@memoize function read_theta13(ndet::Int)
    path = "fit_input/2021_02_03@delcut_third_6.000MeV@bcw/Theta13-inputs_P17B_inclusive_$(ndet)ad.txt"
    return read_theta13(path)
end

