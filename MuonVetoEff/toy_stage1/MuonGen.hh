#pragma once

#include "NewIO.hh"
#include "Sequencer.hh"
#include "Util.hh"

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
  MuonTree(TTree* tree, IOMode mode) :
    TreeWrapper(tree, mode)
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
  std::tuple<TTimeStamp, MuonEvent> next() override;

private:
  int det_;
  float rate_hz_;
  float strength_;
  TTimeStamp last_ = {0, 0};
};

MuonSource::MuonSource(int det, float rate_hz, float strength) :
  det_(det), rate_hz_(rate_hz), strength_(strength) {}

std::tuple<TTimeStamp, MuonEvent> MuonSource::next()
{
  double tToNext_s = ran().Exp(1/rate_hz_);
  shift_timestamp(last_, tToNext_s);
  return {last_,
          {det_,
           UInt_t(last_.GetSec()),
           UInt_t(last_.GetNanoSec()),
           strength_}};
}

using MuonSink = TreeSink<MuonTree>;
