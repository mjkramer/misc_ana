#pragma once

#include "Constants.hh"

#include "Framework/SyncReader.hh"
#include "Framework/BaseIO.hh"
#include "Framework/Util.hh"

class MuonTree : public TreeBase {
public:
  Det detector;
  UInt_t trigSec;
  UInt_t trigNanoSec;
  Float_t strength;             // charge (AD) or nhit (WP)

  Time time() const { return {trigSec, trigNanoSec}; }
  bool inAD() const { return detector <= Det::AD4; }
  bool inWP() const { return detector == Det::IWS || detector == Det::OWS; }

  void initBranches() override;
};

class MuonReader : public SyncReader<MuonTree> {
public:
  MuonReader() : SyncReader({"muons"}) {}
};
