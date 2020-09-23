#include "MuonCondenser.hh"

#include <TH1F.h>
#include <TROOT.h>

static constexpr float WP_MERGE_US = 5;
static constexpr float AD_RETRIG_US = 60;

Algorithm::Status MuonCondenser::consume(const MuonReader::Data& muon)
{
  if (muon.inWP()) {
    for (int idet = 0; idet < 4; ++idet) {

      if (muon.time().diff_us(lastAdTime[idet]) > WP_MERGE_US) {

        if (muon.time().diff_us(lastWpTime[idet]) > WP_MERGE_US) {
          h_wpMuons[idet]->Fill(muon.strength);
        }

        else if (muon.detector != lastWpDet[idet] &&
                 muon.strength > lastWpNhit[idet]) {
          h_wpMuons[idet]->Fill(lastWpNhit[idet], -1);
          h_wpMuons[idet]->Fill(muon.strength);
        }

        else continue;

        lastWpTime[idet] = muon.time();
        lastWpDet[idet] = muon.detector;
        lastWpNhit[idet] = muon.strength;
      }
    }
  }

  else if (muon.inAD()) {
    const int idet = int(muon.detector) - 1;

    if (muon.time().diff_us(lastAdTime[idet]) > AD_RETRIG_US) {
      h_adMuons[idet]->Fill(muon.strength);

      if (muon.time().diff_us(lastWpTime[idet]) < WP_MERGE_US) {
        h_wpMuons[idet]->Fill(lastWpNhit[idet], -1);
      }
    }

    lastAdTime[idet] = muon.time();
  }

  return Status::Continue;
}

MuonCondenser::MuonCondenser()
{
  for (int idet = 0; idet < 4; ++idet) {
    auto wpName = Form("h_wpMuons_ad%d", idet+1);
    auto wpTitle = Form("WP-only muons for AD%d", idet+1);
    h_wpMuons[idet] = new TH1F(wpName, wpTitle, 200, 0, 200);
    h_wpMuons[idet]->SetXTitle("Nhit");

    auto adName = Form("h_adMuons_ad%d", idet+1);
    auto adTitle = Form("AD muons, AD%d", idet+1);
    h_adMuons[idet] = new TH1F(adName, adTitle, 1000, 0, 1e6);
    h_adMuons[idet]->SetXTitle("Charge [p.e.]");
  }
}

void MuonCondenser::finalize(Pipeline& _p)
{
  for (int idet = 0; idet < 4; ++idet) {
    if (h_adMuons[idet]->GetEntries()) {
      h_wpMuons[idet]->Write();
      h_adMuons[idet]->Write();
    }
  }
}
