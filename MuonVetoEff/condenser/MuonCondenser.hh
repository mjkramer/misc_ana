#pragma once

#include "MuonReader.hh"

#include "Framework/SimpleAlg.hh"

class TH1F;

class MuonCondenser : public SimpleAlg<MuonReader> {
public:
  MuonCondenser();
  void finalize(Pipeline& _p) override;
  Status consume_old(const MuonReader::Data& muon);
  Status consume(const MuonReader::Data& muon) override;

private:
  TH1F* h_wpMuons[4];
  TH1F* h_adMuons[4];

  Time lastWpTime[4];
  Det lastWpDet[4];
  UInt_t lastWpNhit[4];

  Time lastAdTime[4];
};
