#pragma once

#include "Framework/BaseIO.hh"
#include "Framework/Util.hh"

class AdTree : public TreeBase {
public:
  UInt_t trigSec;
  UInt_t trigNanoSec;
  Float_t energy;

  UInt_t trigNo;
  UInt_t runNo;
  UShort_t fileNo;

  Float_t x;
  Float_t y;
  Float_t z;

  Time time() const { return { trigSec, trigNanoSec }; }

  void initBranches() override;
};
