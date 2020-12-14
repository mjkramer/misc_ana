#pragma once

#include "AdBuffer.hh"
#include "MuonAlg.hh"

class Config;
class MultCutTool;

class SelectorBase : public BufferedSimpleAlg<AdBuffer, Det> {
public:
  using Iter = AdBuffer::Iter;

  SelectorBase(Det det, MuonAlg::Purpose purpose);

  void connect(Pipeline& p) override;
  Algorithm::Status consume_iter(Iter it) final;
  const AdTree& getCurrent() const // for logging purposes
  {
    return *current;
  }

  virtual void initCuts(const Config* config) = 0;
  virtual void select(Iter it) = 0;

  const Det det;

protected:
  const MuonAlg* muonAlg;
  const MultCutTool* multCut;

private:
  const MuonAlg::Purpose purpose;
  Iter current;
};
