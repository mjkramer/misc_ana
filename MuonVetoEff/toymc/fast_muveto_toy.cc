#include <TRandom3.h>

#include <vector>

struct FastMuVetoToy {
  FastMuVetoToy();

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

  std::vector<Muon> gen_muons(double r_wp, double r_ad, double r_sh);

  double window_size(const Muon& mu) const;
  MuonType select_type(double r_wp, double r_ad, double r_sh);
  double time_to_next(double r_wp, double r_ad, double r_sh);
};

FastMuVetoToy::FastMuVetoToy()
{
  ran.SetSeed();
}

double FastMuVetoToy::window_size(const Muon& mu) const
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

FastMuVetoToy::MuonType
FastMuVetoToy::select_type(double r_wp, double r_ad, double r_sh)
{
  const double div_wp_ad = r_wp / (r_wp + r_ad + r_sh);
  const double div_ad_sh = (r_wp + r_ad) / (r_wp + r_ad + r_sh);
  const double x = ran.Uniform();

  if (x < div_wp_ad)
    return MuonType::Wp;
  else if (x < div_ad_sh)
    return MuonType::Ad;
  else
    return MuonType::Sh;
}

double FastMuVetoToy::time_to_next(double r_wp, double r_ad, double r_sh)
{
  const double tau = 1 / (r_wp + r_ad + r_sh);
  return ran.Exp(tau);
}

std::vector<FastMuVetoToy::Muon>
FastMuVetoToy::gen_muons(double r_wp, double r_ad, double r_sh)
{
  std::vector<Muon> muons;
  double now = 0;

  while (now < livetime) {
    const MuonType type = select_type(r_wp, r_ad, r_sh);
    now += time_to_next(r_wp, r_ad, r_sh);
    muons.push_back({type, now});
  }

  return muons;
}

double FastMuVetoToy::vetoEff(double r_wp, double r_ad, double r_sh)
{
  std::vector<Muon> muons = gen_muons(r_wp, r_ad, r_sh);

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
