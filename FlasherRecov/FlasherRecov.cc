#include "FlasherRecov.hh"

#include <TH2F.h>

extern Site gSite;
extern Phase gPhase;

FlasherRecov::FlasherRecov()
{
  for (Det det : util::ADsFor(gSite, gPhase)) {
    auto name = Form("h2_postFlasher_AD%d", int(det));
    auto title = Form("Event energy vs time since last flasher, EH%d-AD%d",
                      gSite, int(det));
    hists[det] = new TH2F(name, title, 240, 0, 12, 200, 0, 200);
    hists[det]->SetXTitle("Energy [MeV]");
    hists[det]->SetYTitle("Time since last flasher [ms]");
  }
}

void FlasherRecov::connect(Pipeline &pipeline)
{
  muonAlg = pipeline.getAlg<MuonAlg>();

  SimpleAlg::connect(pipeline);
}

Algorithm::Status FlasherRecov::consume(const EventReader::Data &e)
{
  flushPending();

  if (e.isAD()) {
    pending.push({e.det(), e.time(), e.energy, isFlasher(e)});
  }

  return Status::Continue;
}

void FlasherRecov::flushPending()
{
  while (not pending.empty()) {
    const Trig& trig = pending.front();
    const auto status = muonAlg->vetoStatus(trig.det, trig.t);

    if (status == MuonAlg::VetoStatus::Wait)
      break;

    if (status == MuonAlg::VetoStatus::Keep)
      process(trig);

    pending.pop();
  }
}

void FlasherRecov::process(const Trig& trig)
{
  if (trig.flasher) {
    lastFlasher[trig.det] = trig.t;
  } else {
    if (lastFlasher[trig.det] != Time{0, 0}) {
      const float dt_ms = 1e-3 * trig.t.diff_us(lastFlasher[trig.det]);
      hists[trig.det]->Fill(trig.energy, dt_ms);
    }
  }
}

bool FlasherRecov::isFlasher(const EventReader::Data& e)
{
#define SQ(x) pow(x, 2)

  return SQ(e.Quadrant) + SQ(e.MaxQ / 0.45) > 1 ||
    4*SQ(1 - e.time_PSD) + 1.8*SQ(1 - e.time_PSD1) > 1 ||
    e.MaxQ_2inchPMT > 100;

#undef SQ
}

void FlasherRecov::finalize(Pipeline &pipeline)
{
  flushPending();

  for (Det det : util::ADsFor(gSite, gPhase))
    hists[det]->Write();
}
