#include <TRandom3.h>

class AccUncMC {
public:
  struct Params {
    double promptMin, promptMax;
    double delayedMin, delayedMax;
    double vetoEff;
    double livetime_s;
  };

  struct State {
    double nPromptLike;
    double nDelayedLike;
    double nPreMuon;
  };

  AccUncMC(const Params& pars, const State& nominalState);
  double accDaily() const;
  double randAccDaily();

private:
  static constexpr double DT_MAX_US = 200;
  static constexpr double PRE_WINDOW_US = 400;
  static constexpr double POST_WINDOW_US = 200;

  void newState();

  const Params pars_;
  const State nominalState_;
  State state_;

  TRandom3 ran_;
};
