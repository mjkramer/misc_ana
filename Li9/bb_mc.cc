#include <TH1F.h>
#include <TMath.h>
#include <TRandom3.h>

constexpr float LIFETIME = 10e-3;
constexpr float COINCTIME = 200e-6;
constexpr int NEVENTS = 1'000'000;

void bb_mc(TH1F* h)
{
  TRandom3 ran;
  ran.SetSeed();

  for (int i = 0; i < NEVENTS; ++i) {
    const float t1 = ran.Exp(LIFETIME);
    const float t2 = ran.Exp(LIFETIME);

    if (TMath::Abs(t2 - t1) < COINCTIME) {
      h->Fill(TMath::Min(t1, t2));
    }
  }
}
