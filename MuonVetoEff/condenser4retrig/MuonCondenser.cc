#include "MuonCondenser.hh"

#include <TH2F.h>
#include <TROOT.h>

MuonCondenser::MuonCondenser()
{
  for (int icut = 0; icut < N_CUTS_AD; ++icut) {
    for (int idet = 0; idet < 4; ++idet) {
      auto name = Form("h_adToAd_%dpe_ad%d", int(CUTS_PE_AD[icut]), idet+1);
      h_adToAd[icut][idet] = new TH2F(name, name, 25, 0, 25000,
                                      50, 0, 50);
    }
  }

  for (int ipool = 0; ipool < 2; ++ipool) {
    for (int idet = 0; idet < 4; ++idet) {
      auto poolname = ipool == 0 ? "Iwp" : "Owp";
      auto name = Form("h_%sToAd_ad%d", poolname, idet+1);
      h_wpToAd[ipool][idet] = new TH2F(name, name, 25, 0, 25000,
                                       50, 0, 50);
    }
  }

  for (int idet = 0; idet < 4; ++idet) {
    for (int ipool = 0; ipool < 2; ++ipool) {
      auto poolname = ipool == 0 ? "Iwp" : "Owp";
      auto name = Form("h_adTo%s_ad%d", poolname, idet+1);
      h_adToWp[idet][ipool] = new TH2F(name, name, 50, 0, 50,
                                       50, 0, 50);
    }
  }

  for (int ipoolFrom = 0; ipoolFrom < 2; ++ipoolFrom) {
    for (int ipoolTo = 0; ipoolTo < 2; ++ipoolTo) {
      auto poolnameFrom = ipoolFrom == 0 ? "Iwp" : "Owp";
      auto poolnameTo = ipoolTo == 0 ? "Iwp" : "Owp";
      auto name = Form("h_%sTo%s", poolnameFrom, poolnameTo);
      h_wpToWp[ipoolFrom][ipoolTo] = new TH2F(name, name, 50, 0, 50,
                                              50, 0, 50);
    }
  }
}

Algorithm::Status MuonCondenser::consume(const MuonReader::Data& muon)
{
  if (muon.inWP() and muon.strength > 12) {
    int ipool = int(muon.detector) - 5;
    for (int idet = 0; idet < 4; ++idet) {
      auto dt_us = muon.time().diff_us(lastAdTime[0][idet]);
      h_adToWp[idet][ipool]->Fill(muon.strength, dt_us);
    }
    for (int ipoolFrom = 0; ipoolFrom < 2; ++ipoolFrom) {
      auto dt_us = muon.time().diff_us(lastWpTime[ipoolFrom]);
      h_wpToWp[ipoolFrom][ipool]->Fill(muon.strength, dt_us);
    }
    lastWpTime[ipool] = muon.time();
  }

  else if (muon.inAD() and muon.strength > CUTS_PE_AD[0]) {
    int idet = int(muon.detector) - 1;
    for (int icut = 0; icut < N_CUTS_AD; ++icut) {
      auto dt_us = muon.time().diff_us(lastAdTime[icut][idet]);
      h_adToAd[icut][idet]->Fill(muon.strength, dt_us);
    }
    for (int ipool = 0; ipool < 2; ++ipool) {
      auto dt_us = muon.time().diff_us(lastWpTime[ipool]);
      h_wpToAd[ipool][idet]->Fill(muon.strength, dt_us);
    }
    for (int icut = 0; icut < N_CUTS_AD; ++icut) {
      if (muon.strength > CUTS_PE_AD[icut]) {
        lastAdTime[icut][idet] = muon.time();
      }
    }
  }

  return Status::Continue;
}

void MuonCondenser::finalize(Pipeline& _p)
{
  for (int idet = 0; idet < 4; ++idet) {
    if (h_adToAd[0][idet]->GetEntries()) {
      for (int icut = 0; icut < N_CUTS_AD; ++icut)
        h_adToAd[icut][idet]->Write();
      for (int ipool = 0; ipool < 2; ++ipool) {
        h_wpToAd[ipool][idet]->Write();
        h_adToWp[idet][ipool]->Write();
      }
    }
  }

  for (int ipoolFrom = 0; ipoolFrom < 2; ++ipoolFrom) {
    for (int ipoolTo = 0; ipoolTo < 2; ++ipoolTo) {
      h_wpToWp[ipoolFrom][ipoolTo]->Write();
    }
  }
}
