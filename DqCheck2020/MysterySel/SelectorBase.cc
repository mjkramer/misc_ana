#include "MultCut.hh"
#include "SelectorBase.hh"

SelectorBase::SelectorBase(Det det, MuonAlg::Purpose purpose) :
  BufferedSimpleAlg<AdBuffer, Det>(det),
  det(det),
  purpose(purpose) {}

void SelectorBase::connect(Pipeline &p)
{
  BufferedSimpleAlg<AdBuffer, Det>::connect(p);

  muonAlg = p.getAlg<MuonAlg>(purpose);
  ASSERT(muonAlg->rawTag() == int(purpose));

  multCut = p.getTool<MultCutTool>();

  const Config* config = p.getTool<Config>();
  initCuts(config);
}

inline
Algorithm::Status SelectorBase::consume_iter(Iter it)
{
  current = it;
  select(it);
  return Status::Continue;
}

