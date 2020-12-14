#include "MysterySel.hh"
#include "MultCut.hh"
#include "MuonAlg.hh"

#include "Framework/Assert.hh"
#include "Framework/ConfigTool.hh"

#include <TH1F.h>

MysterySel::MysterySel(Det det) :
  SelectorBase(det, MuonAlg::Purpose::ForSingles)
{
  auto hname = Form("h_single_AD%d", int(det));
  // Use fine binning since we're doing integrals in Calculator
  // Go up to 20 MeV so we can calc pre-muon rate (for debugging)
  hist = new TH1F(hname, hname, 2000, 0, 20);
}

void MysterySel::initCuts(const Config *config)
{
  EMIN = config->get<float>("singleEmin", 0.7);
  // No upper limit (we want premuons):
  EMAX = config->get<float>("singleEmax", 99999);
}

void MysterySel::finalize(Pipeline& _p)
{
  hist->Write();
}

void MysterySel::select(Iter it)
{
  if (EMIN < it->energy && it->energy < EMAX &&
      not muonAlg->isVetoed(it->time(), det) &&
      multCut->singleDmcOk(it, det)) {

    hist->Fill(it->energy);
  }
}
