#include <TRandom3.h>

#include <algorithm>
#include <vector>

struct MuVetoToy {
  double vetoEff(double r_wp, double r_ad, double r_sh);

  double livetime = 1e6; // seconds

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

  TRandom3 ran;

  float window_size(const Muon& mu) const;
  void insert_muons(std::vector<Muon>& muons, MuonType type, double rate);
};

float MuVetoToy::window_size(const Muon& mu) const
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

void MuVetoToy::insert_muons(std::vector<Muon>& muons, MuonType type, double rate)
{
  const int N = int(livetime * rate);

  for (int i = 0; i < N; ++i) {
    double time = ran.Uniform(0, livetime);
    muons.push_back({type, time});
  }
}

double MuVetoToy::vetoEff(double r_wp, double r_ad, double r_sh)
{
  std::vector<Muon> muons;

  insert_muons(muons, MuonType::Wp, r_wp);
  insert_muons(muons, MuonType::Ad, r_ad);
  insert_muons(muons, MuonType::Sh, r_sh);

  std::sort(begin(muons), end(muons),
            [](const Muon& a, const Muon& b) { return a.time < b.time; });

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

  return 1 - totalVetoTime / livetime;
}
