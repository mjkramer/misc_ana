#include <TRandom3.h>

#include <algorithm>
#include <vector>

struct MuVetoToy {
  double vetoEff(double r_wp, double r_ad, double r_sh);

  static constexpr double LIVETIME = 1e6; // seconds

  enum class MuonType {
    Wp, Ad, Sh
  };

  struct Muon {
    MuonType type;
    double time;

    float window_size() const
    {
      switch (type) {
      case MuonType::Wp:
        return 602e-6;
      case MuonType::Ad:
        return 1402e-6;
      case MuonType::Sh:
        return 0.4004;
      }
      throw;
    }
  };

  TRandom3 ran;

  void insert_muons(std::vector<Muon>& muons, MuonType type, double rate);
};

void MuVetoToy::insert_muons(std::vector<Muon>& muons, MuonType type, double rate)
{
  const int N = int(LIVETIME * rate);

  for (int i = 0; i < N; ++i) {
    double time = ran.Uniform(0, LIVETIME);
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
    double windowEnd = muon.time + muon.window_size();
    if (windowEnd < lastWindowEnd)
      continue;
    double overlap = muon.time < lastWindowEnd
      ? lastWindowEnd - muon.time
      : 0;
    totalVetoTime += muon.window_size() - overlap;
    lastWindowEnd = windowEnd;
  }

  return 1 - totalVetoTime / LIVETIME;
}
