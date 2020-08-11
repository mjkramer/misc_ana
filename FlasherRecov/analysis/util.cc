#include <TH2F.h>

void norm_h2(TH2F* h)
{
  for (int ybin = 1; ybin <= h->GetNbinsY(); ++ybin) {
    double integral = h->Integral(1, h->GetNbinsX(), ybin, ybin);

    for (int xbin = 1; xbin <= h->GetNbinsX(); ++xbin) {
      double content = 1/integral * h->GetBinContent(xbin, ybin);
      h->SetBinContent(xbin, ybin, content);
    }
  }
}
