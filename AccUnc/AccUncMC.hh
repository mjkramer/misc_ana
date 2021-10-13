#pragma once

#include <TH1F.h>
#include <TRandom3.h>

class AccUncMC {
public:
  struct Params {
    double promptMin, promptMax;
    double delayedMin, delayedMax;
    double isolEminBefore, isolEmaxBefore;
    double isolEminAfter, isolEmaxAfter;
    double dmcEminBefore, dmcEmaxBefore;
    double dmcEminAfter, dmcEmaxAfter;
    double vetoEffSingles;
    double livetime_s;
  };

  AccUncMC(const Params& pars, const TH1F& hSingMeas);
  double accDaily() const;
  double randAccDaily();
  double accDailyUnc(size_t samples=10000);
  void fluctuate();
  void reset();

private:
  static constexpr double DT_MAX_US = 200;
  static constexpr double PRE_WINDOW_US = 400;
  static constexpr double POST_WINDOW_US = 200;

  double singlesCount(double emin, double emax) const;
  double isolEff() const;
  double calcHz(double emin, double emax) const;
  double dmcEff() const;

  const Params pars_;
  TH1F hSingNom_;
  TH1F hSing_;

  TRandom3 ran_;
};
