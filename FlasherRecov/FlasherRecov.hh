#pragma once

#include "EventReader.hh"
#include "MuonAlg.hh"
#include "arr_map.hh"

#include "SelectorFramework/core/SimpleAlg.hh"

#include <queue>

class TH2F;

class FlasherRecov : public SimpleAlg<EventReader> {
public:
  FlasherRecov();

  void connect(Pipeline& pipeline) override;
  Status consume(const EventReader::Data& e) override;
  void finalize(Pipeline& pipeline) override;

  struct Trig {                 // should be private but rootcling no likey
    Det det;
    Time t;
    float energy;
    bool flasher;
  };

private:
  bool isFlasher(const EventReader::Data& e);
  void flushPending();
  void process(const Trig& trig);

  util::arr_map<Time, MAXDET> lastFlasher;
  std::queue<Trig> pending;

  MuonAlg* muonAlg = nullptr;

  util::arr_map<TH2F*, MAXDET> hists;
};
