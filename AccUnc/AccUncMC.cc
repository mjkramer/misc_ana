#include "AccUncMC.hh"

#include "external/FukushimaLambertW.hh"

#include <TH1F.h>

#include <cassert>

static double fine_integral(TH1F* h, double x1, double x2)
{
  const int bin1 = h->FindBin(x1);
  const double frac1 =
    1 - ((x1 - h->GetBinLowEdge(bin1)) / h->GetBinWidth(bin1));

  const int bin2 = h->FindBin(x2);
  const double frac2 =
    bin2 == bin1
    ? -(1 - (x2 - h->GetBinLowEdge(bin2)) / h->GetBinWidth(bin2))
    : (x2 - h->GetBinLowEdge(bin2)) / h->GetBinWidth(bin2);

  const double middle_integral =
    bin2 - bin1 < 2
    ? 0
    : h->Integral(bin1 + 1, bin2 - 1);

  return
    frac1 * h->GetBinContent(bin1) +
    middle_integral +
    frac2 * h->GetBinContent(bin2);
}

AccUncMC::AccUncMC(const Params& pars, const State& nominalState) :
  pars_(pars), nominalState_(nominalState), state_(nominalState)
{}

void AccUncMC::newState()
{
  auto gen = [this](double n) { return ran_.PoissonD(n); };

  state_.nPreMuon = gen(nominalState_.nPreMuon);
  state_.nDelayedLike = gen(nominalState_.nDelayedLike);

  const double n0to6 = gen(nominalState_.nPromptLike - nominalState_.nDelayedLike);
  state_.nPromptLike = n0to6 + state_.nDelayedLike;
}

double AccUncMC::isolEff() const
{
  const double nBefore = state_.nPromptLike + state_.nPreMuon;
  const double nAfter = state_.nDelayedLike;
  const double tBefore_s = 1e-6 * PRE_WINDOW_US;
  const double tAfter_s = 1e-6 * POST_WINDOW_US;
  const double denom = pars_.vetoEff * pars_.livetime_s;

  const double arg =
    ((nBefore * tBefore_s) + (nAfter * tAfter_s)) / denom;

  return exp(Fukushima::LambertW0(-arg));
}

double AccUncMC::calcHz(double n) const
{
  return n / (isolEff() * pars_.vetoEff * pars_.livetime_s);
}

double AccUncMC::dmcEff() const
{
  // XXX Do the DMC and isolation cuts use consistent prompt/delayed ranges? No!!!
  const double rPrompt = calcHz(state_.nPromptLike);
  const double rDelayed = calcHz(state_.nDelayedLike);
  const double rPreMuon = calcHz(state_.nPreMuon);
  const double rPlus = rPrompt + rPreMuon;

  const double tBefore_s = 1e-6 * PRE_WINDOW_US;
  const double tAfter_s = 1e-6 * POST_WINDOW_US;

  const double arg = (rPlus * tBefore_s) + (rDelayed * tAfter_s);
  return exp(-arg);
}

double AccUncMC::accDaily() const
{
  const double rPrompt = calcHz(state_.nPromptLike);
  const double rDelayed = calcHz(state_.nDelayedLike);
  const double rPreMuon = calcHz(state_.nPreMuon);
  const double rPlus = rPrompt + rPreMuon;

  const double promptWin_s = 1e-6 * DT_MAX_US;
  const double voidBeforePromptWin_s = (1e-6 * PRE_WINDOW_US) - promptWin_s;
  const double voidAfterDelayed_s = 1e-6 * POST_WINDOW_US;

  const double probOnePromptInPromptWin =
    rPrompt * promptWin_s * exp(-rPrompt * promptWin_s);
  const double probZeroPreMuonInPromptWin =
    exp(-rPreMuon * promptWin_s);
  const double probZeroPlusInVoidBeforePromptWin =
    exp(-rPlus * voidBeforePromptWin_s);
  const double probZeroDelayedInVoidAfterDelayed =
    exp(-rDelayed * voidAfterDelayed_s);

  const double R = rDelayed * probOnePromptInPromptWin *
    probZeroPreMuonInPromptWin * probZeroPlusInVoidBeforePromptWin *
    probZeroDelayedInVoidAfterDelayed;

  // This R assumes veto eff. of 1 (i.e. unreduced by it) while R IS
  // reduced by DMC eff by construction (i.e. we are predicting what we'd see
  // in the RAW spectrum, modulo veto eff.). In the fitter, we multiply every
  // bkg rate by the veto and DMC efficiencies (*for IBDs*), prior to
  // subtracting from the raw IBD spectrum(?). Therefore, here we must divide by
  // the DMC efficiency for IBDs, to pre-cancel-out this multiplication.

  const double hzToDaily = 86'400;
  return hzToDaily * R / dmcEff();
}
