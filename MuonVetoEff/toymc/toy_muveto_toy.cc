#include <TFile.h>
#include <TH1F.h>
#include <TTree.h>

#include <algorithm>
#include <vector>

struct ToyMuVetoToy {
  ToyMuVetoToy();

  double vetoEff(const char* stage1_path, int det=1);

  double tVetoWp = 602e-6;
  double tVetoAd = 1402e-6;
  double tVetoSh = 0.4004;

  enum class MuonType {
    Wp, Ad, Sh
  };

  struct Muon {
    MuonType type;
    double time;

  };

  float window_size(const Muon& mu) const;
  void insert_muons(std::vector<Muon>& muons, TFile& stage1_file, int det=1);
};

ToyMuVetoToy::ToyMuVetoToy()
{
}

float ToyMuVetoToy::window_size(const Muon& mu) const
{
  switch (mu.type) {
  case MuonType::Wp:
    return tVetoWp;
  case MuonType::Ad:
    return tVetoAd;
  case MuonType::Sh:
    return tVetoSh;
  }
  throw;
}

void ToyMuVetoToy::insert_muons(std::vector<Muon>& muons, TFile& stage1_file, int det)
{
  auto tree = (TTree*) stage1_file.Get("muons");

  Int_t detector;
  UInt_t trigSec;
  UInt_t trigNanoSec;
  Float_t strength;

  tree->SetBranchAddress("detector", &detector);
  tree->SetBranchAddress("trigSec", &trigSec);
  tree->SetBranchAddress("trigNanoSec", &trigNanoSec);
  tree->SetBranchAddress("strength", &strength);

  for (int i = 0; tree->GetEntry(i); ++i) {
    double time = trigSec + 1e-9*trigNanoSec;

    if ((detector == 5 || detector == 6) &&
        strength > 12) {
      muons.push_back({MuonType::Wp, time});
    } else if (detector == det && strength > 3e5) {
      muons.push_back({MuonType::Sh, time});
    } else if (detector == det && strength > 3000) {
      muons.push_back({MuonType::Ad, time});
    }
  }
}

double ToyMuVetoToy::vetoEff(const char* stage1_path, int det)
{
  std::vector<Muon> muons;

  TFile stage1_file(stage1_path);
  insert_muons(muons, stage1_file);

  double lastWindowEnd = 0;
  double totalVetoTime = 0;

  for (const auto& muon : muons) {
    double windowEnd = muon.time + window_size(muon);
    if (windowEnd < lastWindowEnd)
      continue;
    double overlap = muon.time < lastWindowEnd
      ? lastWindowEnd - muon.time
      : 0;
    totalVetoTime += window_size(muon) - overlap;
    lastWindowEnd = windowEnd;
  }

  auto h_livetime = (TH1F*) stage1_file.Get("h_livetime");
  const float livetime = h_livetime->GetBinContent(1);

  return 1 - totalVetoTime / livetime;
}
