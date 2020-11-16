#pragma once

#include "NewIO.hh"

struct MuonEvent {
  Int_t detector;
  UInt_t trigSec;
  UInt_t trigNanoSec;
  Float_t strength;
};

struct MuonTree : virtual TreeWrapper<MuonEvent> {
  void init() override
  {
    NEW_BR(detector);
    NEW_BR(trigSec);
    NEW_BR(trigNanoSec);
    NEW_BR(strength);
  };
};

struct AdEvent {
  UInt_t trigSec;
  UInt_t trigNanoSec;
  Float_t energy;

  UInt_t trigNo;
  UInt_t runNo;
  UShort_t fileNo;
};

struct AdTree : virtual TreeWrapper<AdEvent> {
  void init() override
  {
    NEW_BR(trigSec);
    NEW_BR(trigNanoSec);
    NEW_BR(energy);

    NEW_BR(trigNo);
    NEW_BR(runNo);
    NEW_BR(fileNo);
  }
};
