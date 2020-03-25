using PyCall
using DataFrames
using UpROOT
using TypedTables

f_short = abspath(ENV["SCRATCH"], "tmp/short.calib.21221.root")
f_mine = abspath(ENV["SCRATCH"], "tmp/calib.21221.root")
f_p17b = read(`p17b_find 21221 1`, String) |> chop

function read_ttree(tree::TTree, branchnames::Array{<:AbstractString})
    tree_data = UpROOT.pyobj(tree).arrays(branchnames)

    df = DataFrame()
    for bn in branchnames
        # Silence warning
        # df[Symbol(bn)] = UpROOT.py2jl(tree_data[bn])
        df[!, Symbol(bn)] = UpROOT.py2jl(tree_data[bn])
    end

    df
end

branches_of(tree::TTree) = [String(k) for k in keys(t[1])]
read_ttree(tree::TTree) = read_ttree(tree, branches_of(tree))

fn = f_short
# f = TFile(fn)
# t = f["Event/Data/CalibStats"]

fn2 = "/global/homes/m/mkramer/mywork/ThesisAnalysis/IbdSel/data/stage2_pbp/2020_01_26@yolo2/stage2.pbp.eh1.6ad.root"
f2 = TFile(fn2)
t2 = f2["results"]

cols(t) = UpROOT.pyobj(t).arrays(entrystart = 0, entrystop = 1)
to_tab(t) = Table(UpROOT._dict2nt(cols(t)))

function Base.getindex(tree::TTree, idxs::AbstractUnitRange)
    @boundscheck checkbounds(tree, idxs)
    cols = UpROOT.pyobj(tree).arrays(entrystart = first(idxs) - 1, entrystop = last(idxs))
    # hack to get rid of static-sized arrays:
    cols = Dict(k => v for (k, v) in cols
                if findfirst("[", k) === nothing)

    Table(_dict2nt(cols)) # fails if branches aren't all the same length
end

_dict2nt(d::Dict) = NamedTuple{Tuple(Symbol.(keys(d)))}(py2jl.(values(d)))

# c = cols(t)

d = Dict(1 => 2, 3 => 4)

for (k, v) in d
    print(k)
    print(v)
end

goodcols = filter(p -> (typeof(p.second) <: Array), c)
weirdcols = filter(p -> !(typeof(p.second) <: Array), c)

d = Base.Multimedia.displays[2]
d.repl.options.iocontext

show(IOContext(stdout, :limit => true, :displaysize => (100, 80)),
     MIME"text/plain"(),
     goodcols)

d = Dict()
for (k, v) in collect(goodcols)[1:2]
    println(k)
    # d = Dict(k => v)
    d[k] = v
end
Table(_dict2nt(d))

Table(_dict2nt(Dict(collect(goodcols)[1:2])))

# TypedTables._ndims(x) = 1
