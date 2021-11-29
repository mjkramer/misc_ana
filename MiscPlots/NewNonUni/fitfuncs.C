// stolen from dquiri/scripts/build_db

#include <math.h>               // conda's root 6.05/02 doesn't like <cmath>
#include <TMath.h>

#define SQ(x) ((x)*(x))

// Jianrun's function for fitting K40 and Tl208
// See /dybfs/users/hujianrun/P17BEnergyCheck/Final_source_energy/{K40,Tl208}/reconstru.C
// ... copied in refs/reconstru_{K40,Tl208}.C
double powgaus(double* x, double* par)
{
  double a = par[0], b = par[1], N = par[2], mu = par[3], sigma = par[4];
  double X = x[0];

  return a / (X*X - b)  +  N * exp(-SQ((X-mu)/sigma) / 2);
}

// Chris's (i.e. Yury's?) DYB function
// See /global/homes/m/marshalc/TDNU/static/fit_staticNU.C
// ... copied in refs/fit_staticNU.C
double mydybf(double* x, double* par)
{
  double N1 = par[0], N2 = par[1], mu = par[2], sigma = par[3];
  double lambda = par[4], a = par[5];
  double X = x[0];
  double k = sqrt(6.283185307);

#define ERF1(d) erf( ((d) - X - lambda*SQ(sigma))  /  (sqrt(2)*sigma) )
#define ERF2(d) erf( ((d) - X)                     /  (sqrt(2)*sigma) )

  double peak = 1/(k*sigma) * exp(-SQ((X-mu)/sigma) / 2);
  double tail1 = lambda/2 * exp(SQ(sigma*lambda) / 2) * exp(lambda*X) *
    (ERF1(mu) - ERF1(0));
  double tail2 = a/2 * (ERF2(mu) - ERF2(0));

  return N1*peak + N2*(tail1+tail2);

#undef ERF1
#undef ERF2
}

double dybf(double *x, double *par)
{
  Double_t N1 = par[0];
  Double_t N2 = par[1];
  Double_t mu = par[2];
  Double_t sigma = par[3];
  Double_t lambda = par[4];
  Double_t a = par[5];

  Double_t X = x[0];

  Double_t f_peak = 1./sqrt(6.283185307)/sigma * TMath::Exp(-(X-mu)*(X-mu)/(2*sigma*sigma));

  Double_t f_tail1 = lambda / 2. * TMath::Exp(sigma*sigma*lambda*lambda/2.) * TMath::Exp(lambda*X) * (
  TMath::Erf((mu-(X+sigma*sigma*lambda))/(sqrt(2)*sigma)) -
  TMath::Erf((0.-(X+sigma*sigma*lambda))/(sqrt(2)*sigma))   );

  Double_t f_tail2 = a/2. * ( TMath::Erf((mu-X)/(sigma*sqrt(2))) - 
                              TMath::Erf((0.-X)/(sigma*sqrt(2)))  );

  return N1*f_peak + N2*(f_tail1 + f_tail2);
}

double _doubdybf_helper(double (*fn)(double*, double*),
                        double *x, double *par)
{
  double N11 = par[0], N21 = par[1], mu1 = par[2], sigma = par[3],
    lambda = par[4], a = par[5];

  double kN = 0.22598, kMu = 1.075566;

  double N12 = kN * N11, N22 = kN * N21;
  double mu2 = kMu * mu1;

  double p1[] = {N11, N21, mu1, sigma, lambda, a};
  double p2[] = {N12, N22, mu2, sigma, lambda, a};

  return fn(x, p1) + fn(x, p2);
}

double doubdybf(double *x, double *par)
{
  return _doubdybf_helper(dybf, x, par);
}

double doubmydybf(double *x, double *par)
{
  return _doubdybf_helper(mydybf, x, par);
}

// single crystal ball helper
inline double singcrys(double arg, double a, double n)
{
  if (arg > -a) {
    return exp(-0.5 * SQ(arg));
  } else {
    double A = pow(n/fabs(a), n) * exp(-0.5 * SQ(a));
    double B = n/fabs(a) - fabs(a);
    return A * pow(B-arg, -n);
  }
}

// double crystal ball, also from Chris's code
double doubcrys(double* x, double* par)
{
  //     norm             alpha       n           mean              sigma
  double N1 = par[0],     a = par[1], n = par[2], m1 = par[3],      s = par[4];
  double N2 = 0.22598*N1,                         m2 = 1.075566*m1;
  double X = x[0];

  double arg1 = s  ?  (X - m1) / s  :  0;
  double arg2 = s  ?  (X - m2) / s  :  0;

  return N1*singcrys(arg1, a, n) + N2*singcrys(arg2, a, n);
}

// what we actually use for nGd
double dcbfPlusExp(double* x, double* par)
{
  return doubcrys(x, par) + exp(par[5] + par[6]*x[0]);
}

#undef SQ
