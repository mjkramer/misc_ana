#include "FlasherAlg.hh"

void FlasherAlg::connect(Pipeline& pipeline)
{
  muonAlg = pipeline.getAlg<MuonAlg>();

  SimpleAlg::connect(pipeline);
}

Algorithm::Status FlasherAlg::consume(const EventReader::Data& e)
{
  if (e.isAD() && is_flasher(e))
    pending.push({e.det(), e.time()});

  flush();

  return Algorithm::Status::Continue;
}

void FlasherAlg::finalize(Pipeline &pipeline)
{
  flush();
}

Time FlasherAlg::last_flasher(Det det)
{
  return lastFlasher[det];
}

bool FlasherAlg::is_flasher(const EventReader::Data& e)
{
#define SQ(x) pow(x, 2)

  return SQ(e.Quadrant) + SQ(e.MaxQ / 0.45) > 1 ||
    4*SQ(1 - e.time_PSD) + 1.8*SQ(1 - e.time_PSD1) > 1 ||
    e.MaxQ_2inchPMT > 100;

#undef SQ
}

void FlasherAlg::flush()
{
  while (not pending.empty()) {
    const Candidate& candi = pending.front();
    const auto status = muonAlg->veto_status(candi.det, candi.t);

    if (status == MuonAlg::VetoStatus::Wait)
      break;

    if (status == MuonAlg::VetoStatus::Keep)
      lastFlasher[candi.det] = candi.t;

    pending.pop();
  }
}
