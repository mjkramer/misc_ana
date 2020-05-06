using TypedTables

# original definition in UpROOT/ttree.jl
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

# added all-branches read_ttree
branches_of(tree::TTree) = [String(k) for k in keys(tree[1])]
read_ttree(tree::TTree) = read_ttree(tree, branches_of(tree))

# fix needed to make Table from CalibStats
# getindex was choking on "jobId.m_data[4]"
# preventing "pretty" printing of tree, etc.
function Base.getindex(tree::TTree, idxs::AbstractUnitRange)
    @boundscheck checkbounds(tree, idxs)
    cols = UpROOT.pyobj(tree).arrays(entrystart = first(idxs) - 1, entrystop = last(idxs))
    # hack to get rid of static-sized arrays:
    cols = Dict(k => v for (k, v) in cols
                if findfirst("[", k) === nothing)

    Table(UpROOT._dict2nt(cols)) # fails if branches aren't all the same length
end

