#pragma once

#include "SelectorBase.hh"

class TH1F;

// -----------------------------------------------------------------------------

class MysterySel : public SelectorBase {
public:
  float EMIN;
  float EMAX;

  MysterySel(Det det);
  void initCuts(const Config* config) override;
  void select(Iter it) override;
  void finalize(Pipeline& p) override;

  TH1F* hist;
};

