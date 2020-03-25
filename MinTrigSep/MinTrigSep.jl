using DataFrames
using UpROOT

include("util.jl")

f_short = abspath(ENV["SCRATCH"], "tmp/short.calib.21221.root")
f_mine = abspath(ENV["SCRATCH"], "tmp/calib.21221.root")
f_p17b = read(`p17b_find 21221 1`, String) |> chop

function read_times(fname)
    file = TFile(fname)
    tree = file["Event/Data/CalibStats"]

    branches = ["context.mDetId",
                "context.mTimeStamp.mSec",
                "context.mTimeStamp.mNanoSec"]

    df = read_ttree(tree, branches)
    rename!(df, ["det", "s", "ns"])
end

function timediffs(df, det)
    dfp = df[df.det .== det, :]
    sel = dfp[!, [:s, :ns]]
    mtx = convert(Matrix, sel)
    deltas2d = mtx[2:end, :] - mtx[1:end-1, :]
    convert(Int, 1e9) * deltas2d[:, 1] + deltas2d[:, 2]
end
