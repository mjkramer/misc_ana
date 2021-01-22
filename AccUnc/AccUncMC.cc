#include "AccUncMC.hh"

#include "external/FukushimaLambertW.hh"

#include <TH1F.h>

#include <cassert>
#include <numeric>
#include <vector>

static double fine_integral(const TH1F& h_, double x1, double x2)
{
  TH1F& h = const_cast<TH1F&>(h_);

  const int bin1 = h.FindBin(x1);
  const double frac1 =
    1 - ((x1 - h.GetBinLowEdge(bin1)) / h.GetBinWidth(bin1));

  const int bin2 = h.FindBin(x2);
  const double frac2 =
    bin2 == bin1
    ? -(1 - (x2 - h.GetBinLowEdge(bin2)) / h.GetBinWidth(bin2))
    : (x2 - h.GetBinLowEdge(bin2)) / h.GetBinWidth(bin2);

  const double middle_integral =
    bin2 - bin1 < 2
    ? 0
    : h.Integral(bin1 + 1, bin2 - 1);

  return
    frac1 * h.GetBinContent(bin1) +
    middle_integral +
    frac2 * h.GetBinContent(bin2);
}

static double stddev(const std::vector<double>& v)
{
  const double mean = std::accumulate(v.begin(), v.end(), 0.0) / v.size();
  const double sq_sum = std::inner_product(v.begin(), v.end(), v.begin(), 0.0,
      [](double acc, double val) { return acc + val; },
      [mean](double x, double y) {
        return (x - mean) * (y - mean); });
  return std::sqrt(sq_sum / v.size());
}

AccUncMC::AccUncMC(const Params& pars, const TH1F& hSingMeas) :
  pars_(pars), hSingNom_(hSingMeas), hSing_(hSingMeas)
{}

void AccUncMC::fluctuate()
{
  for (int bin = 1; bin <= hSingNom_.GetNbinsX(); ++bin) {
    const double nomVal = hSingNom_.GetBinContent(bin);
    const double randVal = ran_.PoissonD(nomVal);
    hSing_.SetBinContent(bin, randVal);
  }
}

double AccUncMC::singlesCount(double emin, double emax) const
{
  return fine_integral(hSing_, emin, emax);
}

double AccUncMC::isolEff() const
{
  const double nBefore = singlesCount(pars_.isolEminBefore, pars_.isolEmaxBefore);
  const double nAfter = singlesCount(pars_.isolEminAfter, pars_.isolEmaxAfter);
  const double tBefore_s = 1e-6 * PRE_WINDOW_US;
  const double tAfter_s = 1e-6 * POST_WINDOW_US;
  const double denom = pars_.vetoEffSingles * pars_.livetime_s;

  const double arg =
    ((nBefore * tBefore_s) + (nAfter * tAfter_s)) / denom;

  return exp(Fukushima::LambertW0(-arg));
}

double AccUncMC::calcHz(double emin, double emax) const
{
  const double n = singlesCount(emin, emax);
  return n / (isolEff() * pars_.vetoEffSingles * pars_.livetime_s);
}

double AccUncMC::dmcEff() const
{
  // XXX Do the DMC and isolation cuts use consistent prompt/delayed ranges? No!!!
  const double rBefore = calcHz(pars_.dmcEminBefore, pars_.dmcEmaxBefore);
  const double rAfter = calcHz(pars_.dmcEminAfter, pars_.dmcEmaxAfter);

  const double tBefore_s = 1e-6 * PRE_WINDOW_US;
  const double tAfter_s = 1e-6 * POST_WINDOW_US;

  const double arg = (rBefore * tBefore_s) + (rAfter * tAfter_s);
  return exp(-arg);
}

double AccUncMC::accDaily() const
{
  const double rPrompt = calcHz(pars_.promptMin, pars_.promptMax);
  const double rDelayed = calcHz(pars_.delayedMin, pars_.delayedMax);
  const double rPreMuon = calcHz(pars_.promptMax, 99999);
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

double AccUncMC::randAccDaily()
{
  fluctuate();
  return accDaily();
}

double AccUncMC::accDailyUnc(size_t samples)
{
  std::vector<double> vals(samples);
  std::generate(vals.begin(), vals.end(),
                [this]() { return randAccDaily(); });
  return stddev(vals);
}
