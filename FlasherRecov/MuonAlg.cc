#include "MuonAlg.hh"

Algorithm::Status MuonAlg::consume(const EventReader::Data& e)
{
  if (e.isWP() && e.nHit > WP_MIN_NHIT) {
    muons.put({Type::WP, e.det(), e.time()});
    return Status::SkipToNext;
  }

  else if (e.isAD()) {
    if (e.energy > SHOWER_MIN_MEV) {
      muons.put({Type::Shower, e.det(), e.time()});
      return Status::SkipToNext;
    }
    else if (e.energy > AD_MIN_MEV) {
      muons.put({Type::AD, e.det(), e.time()});
      return Status::SkipToNext;
    }
  }

  return Status::Continue;
}

MuonAlg::VetoStatus MuonAlg::vetoStatus(Det det, Time t)
{
  if (muons.size() == 0 || t.diff_us(muons.top().t) > -PRE_VETO_US)
    return VetoStatus::Wait;

  for (const Muon& muon : muons) {
    const float dt = t.diff_us(muon.t);

    if (dt > SHOWER_VETO_US)
      break;

    if (muon.type == Type::WP &&
        dt < WP_VETO_US && dt > -PRE_VETO_US)
      return VetoStatus::Veto;

    if (muon.type == Type::AD &&
        dt < AD_VETO_US && dt > -PRE_VETO_US)
      return VetoStatus::Veto;

    if (muon.type == Type::Shower &&
        dt < SHOWER_VETO_US && dt > -PRE_VETO_US)
      return VetoStatus::Veto;
  }

  return VetoStatus::Keep;
}
