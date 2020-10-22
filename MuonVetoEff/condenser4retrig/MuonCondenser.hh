#pragma once

#include "MuonReader.hh"

#include "Framework/SimpleAlg.hh"

class TH2F;

static constexpr float CUTS_PE_AD[] = {3'000, 10'000, 50'000, 1e5, 2e5, 3e5, 4e5, 5e5};
static constexpr int N_CUTS_AD = sizeof(CUTS_PE_AD) / sizeof(CUTS_PE_AD[0]);

class MuonCondenser : public SimpleAlg<MuonReader> {
public:
  MuonCondenser();
  void finalize(Pipeline& _p) override;
  Status consume(const MuonReader::Data& muon) override;

private:
  // XtoY = from _preceding_ X to Y: h[X][Y]
  TH2F* h_adToAd[N_CUTS_AD][4];
  TH2F* h_wpToAd[2][4];
  TH2F* h_adToWp[4][2];         // just 3000 pe
  TH2F* h_wpToWp[2][2];

  Time lastAdTime[N_CUTS_AD][4];
  Time lastWpTime[2];
};
