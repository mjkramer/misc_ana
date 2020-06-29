// XXX delete me

#pragma once

#include "EventReader.hh"
#include "MuonAlg.hh"

#include "SelectorFramework/core/SimpleAlg.hh"

#include <queue>

class FlasherAlg : public SimpleAlg<EventReader> {
public:
  void connect(Pipeline& pipeline) override;
  Status consume(const EventReader::Data& e) override;
  void finalize(Pipeline& pipeline) override;
  Time last_flasher(Det det);

private:
  struct Candidate {
    Det det;
    Time t;
  };

  bool is_flasher(const EventReader::Data& e);
  void flush();

  util::arr_map<Time, MAXDET> lastFlasher;
  std::queue<Candidate> pending;

  MuonAlg* muonAlg = nullptr;
};
