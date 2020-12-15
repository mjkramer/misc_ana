#pragma once

#include "SelectorBase.hh"

class TH2F;
class TH3F;

// -----------------------------------------------------------------------------

class MysterySel : public SelectorBase {
public:
  float EMIN;
  float EMAX;

  MysterySel(Det det);
  void initCuts(const Config* config) override;
  void select(Iter it) override;
  void finalize(Pipeline& p) override;

  TH2F* h2_rz;
  TH2F* h2_r2z;
  TH2F* h2_xy;
  TH3F* h3_xyz;
};

