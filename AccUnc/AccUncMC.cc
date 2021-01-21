#include "AccUncMC.hh"

#include "external/FukushimaLambertW.hh"

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
}
