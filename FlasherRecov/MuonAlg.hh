#pragma once

#include "EventReader.hh"

#include "SelectorFramework/core/RingBuf.hh"
#include "SelectorFramework/core/SimpleAlg.hh"

class MuonAlg : public SimpleAlg<EventReader> {
  // These bounds are exclusive (i.e. compared using >, not >=)
  static constexpr int WP_MIN_NHIT = 12;
  static constexpr float AD_MIN_MEV = 20;
  static constexpr float SHOWER_MIN_MEV = 2000;
  static constexpr float PRE_VETO_US = 2;
  static constexpr float WP_VETO_US = 600;
  static constexpr float AD_VETO_US = 1000;
  static constexpr float SHOWER_VETO_US = 1'000'000;

public:
  enum class VetoStatus { Keep, Veto, Wait };

  Status consume(const EventReader::Data& e) override;
  VetoStatus vetoStatus(Det det, Time t);

// private:
  enum class Type { WP, AD, Shower };

  struct Muon {
    Type type;
    Det det;
    Time t;
  };

private:
  RingBuf<Muon> muons{100};
};
