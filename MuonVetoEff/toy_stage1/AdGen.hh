#pragma once

#include "NewIO.hh"
#include "Sequencer.hh"
#include "Util.hh"

#include <TRandom3.h>

struct AdEvent {
  UInt_t trigSec;
  UInt_t trigNanoSec;
  Float_t energy;

  UInt_t trigNo;
  UInt_t runNo;
  UShort_t fileNo;
};

struct AdTree : virtual TreeWrapper<AdEvent> {
  AdTree(TTree* tree, IOMode mode) :
    TreeWrapper(tree, mode)
  {
    NEW_BR(trigSec);
    NEW_BR(trigNanoSec);
    NEW_BR(energy);

    NEW_BR(trigNo);
    NEW_BR(runNo);
    NEW_BR(fileNo);
  }
};

class SingleSource : virtual public RanEventSource<AdEvent> {
public:
  SingleSource(float rate_hz, float energy);
  std::tuple<TTimeStamp, AdEvent> next() override;

private:
  float rate_hz_;
  float energy_;
  TTimeStamp last_ = {0, 0};
};

SingleSource::SingleSource(float rate_hz, float energy) :
  rate_hz_(rate_hz), energy_(energy) {}

std::tuple<TTimeStamp, AdEvent> SingleSource::next()
{
  double tToNext_s = ran().Exp(1/rate_hz_);
  shift_timestamp(last_, tToNext_s);

  AdEvent e;
  e.trigSec = last_.GetSec();
  e.trigNanoSec = last_.GetNanoSec();
  e.energy = energy_;

  return {last_, e};
}

class IbdSource : virtual public RanEventSource<AdEvent> {
public:
  IbdSource(float rate_hz);
  std::tuple<TTimeStamp, AdEvent> next() override;

private:
  float rate_hz_;
  TTimeStamp last_ = {0, 0};
  bool nextIsDelayed_ = false;
};

IbdSource::IbdSource(float rate_hz) :
  rate_hz_(rate_hz) {}

std::tuple<TTimeStamp, AdEvent> IbdSource::next()
{
  AdEvent e;

  if (nextIsDelayed_) {
    shift_timestamp(last_, 100e-6);
    e.energy = 8;
    nextIsDelayed_ = false;
  }
  else {
    double tToNext_s = ran().Exp(1/rate_hz_);
    shift_timestamp(last_, tToNext_s);
    e.energy = 3;
    nextIsDelayed_ = true;
  }

  e.trigSec = last_.GetSec();
  e.trigNanoSec = last_.GetNanoSec();

  return {last_, e};
}

class AdSink : virtual public TreeSink<AdTree> {
public:
  using TreeSink<AdTree>::TreeSink;
  void prep(AdEvent& event) override;

private:
  UInt_t trigNo_ = 0;
};

void AdSink::prep(AdEvent& event)
{
  event.trigNo = trigNo_++;
  event.runNo = 12345;
  event.fileNo = 1;
}
