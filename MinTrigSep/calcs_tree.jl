using DataFrames
using UpROOT
using DataStructures

include("util.jl")

BASE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/stage2_pbp/2020_01_26@yolo3"
T13_BASE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/fit_input/2020_01_26@yolo3"
T13_LBNL = "/global/u2/m/mkramer/mywork/ThesisAnalysis/samples/beda.mine/example/LBNL"
TESTFILE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/code/selector/stage2.root"
TESTFILE_NEEDMOREBINS = "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/code/selector/stage2_needMoreBins.root"
TESTFILE_OFFBYONE = "/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/code/selector/stage2_offByOne.root"

function pbp_path(hall, nADs)
    "$BASE/stage2.pbp.eh$hall.$(nADs)ad.root"
end

function read_results(path)
    df = TFile(path)["results"] |> read_ttree
    df.seq = Int32.(df.seq)
    cols = [:seq,
            :detector,
            :accDaily,
            :vetoEff,
            :vetoEffSingles,
            :dmcEff,
            :dmcEffSingles,
            :nPlusLikeSingles,
            :nPromptLikeSingles,
            :nDelayedLikeSingles,
            :nPreMuons,
            :plusLikeHz,
            :promptLikeHz,
            :delayedLikeHz,
            :preMuonHz]
    df = df[!, cols]
    renames = Dict(:detector => "det",
                   :vetoEff => "veto",
                   :vetoEffSingles => "vetoSing",
                   :dmcEff => "dmc",
                   :dmcEffSingles => "dmcSing",
                   :nPlusLikeSingles => "nPlus",
                   :nPromptLikeSingles => "nPrompt",
                   :nDelayedLikeSingles => "nDelayed",
                   :plusLikeHz => "hzPlus",
                   :promptLikeHz => "hzPrompt",
                   :delayedLikeHz => "hzDelayed")
    rename!(df, renames)
    df
end

function res(fname)
    read_results("/global/u2/m/mkramer/mywork/ThesisAnalysis/IbdSel/code/selector/$fname")
end

function t13_path(base, nADs, suffix="")
    "$base/Theta13-inputs_P17B_inclusive_$(nADs)ad$suffix.txt"
end

function read_t13(path)
    result = OrderedDict()
    notcomment(line) = !startswith(strip(line), "#")
    lines = filter(notcomment, readlines(path))[begin+3:end]
    for line in lines
        parts = split(line)
        rowcode = parse(Int32, parts[2])
        if rowcode == 0
            continue
        end
        vals = [parse(Float32, v) for v in parts[3:10]]
        result[rowcode] = vals
    end
    result
end

if false

    t13_lbnl = read_t13(t13_path(T13_LBNL, 6, "_LBNL"));
    t13_yolo = read_t13(t13_path(T13_BASE, 6));
    acc_lbnl, acc_yolo = t13_lbnl[11], t13_yolo[11];

end
