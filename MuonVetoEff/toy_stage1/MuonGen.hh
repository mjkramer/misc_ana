#pragma once

#include "NewIO.hh"
#include "Sequencer.hh"

#include <TRandom3.h>

enum class MuonType {
  Wp, Ad, Sh
};

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

class MuonSource : virtual public RanEventSource<MuonEvent> {
public:
  MuonSource(int det, float rate_hz, float strength);
  std::tuple<Time, MuonEvent> next() override;

private:
  int det_;
  float rate_hz_;
  float strength_;
  Time last_;
};

MuonSource::MuonSource(int det, float rate_hz, float strength) :
  det_(det), rate_hz_(rate_hz), strength_(strength) {}

std::tuple<Time, MuonEvent> MuonSource::next()
{
  double tToNext_s = ran().Exp(1/rate_hz_);
  last_ = last_.shifted_us(1e6 * tToNext_s);
  return {last_,
          {det_, last_.s, last_.ns, strength_}};
}

using MuonSink = TreeSink<MuonTree>;
