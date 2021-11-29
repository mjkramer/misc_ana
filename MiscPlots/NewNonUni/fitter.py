#!/usr/bin/env python3

# Taken from /global/cfs/cdirs/dayabay/scratch/mkramer/p17b/dqcheck/rel_escale

MAXTRIES = 50

import ROOT as R

R.gROOT.ProcessLine(".L fitfuncs.C+")


class Fitter:
    def __init__(self, name, func, xmin, xmax, npar):
        self.f = R.TF1(name, func, xmin, xmax, npar)
        self._do_draw = False

    def fit(self, hist):
        "Returns [(par, err), ...], chi2ndf, success (0/1)"
        # prevent from being GC'd in case we want to peek
        # self.last_hist = hist
        tries = 0
        while True:
            # opt = "RS" if self._do_draw else "RSQ0"
            opt = "R" if self._do_draw else "RQN0"
            # resultPtr = hist.Fit(self.f, opt)
            hist.Fit(self.f, opt)
            # resultPtr = hist.Fit(self.f, "RS")
            # result = resultPtr.Get()
            tries += 1

            status = R.gMinuit.fCstatu.replace(" ", "")
            valid = (status == 'CONVERGED'
                     or status == 'OK'
                     or status == 'NOTPOSDEF')
            success = 1
            if valid or tries == MAXTRIES:
                if tries == MAXTRIES:
                    print('Fit failure!', self.f.GetName())
                    success = 0
                buf, buf_e = self.f.GetParameters(), self.f.GetParErrors()
                for b in [buf, buf_e]:
                    # older ROOT: b.SetSize(f.GetNpar())
                    b.reshape((self.f.GetNpar(),))
                chi2ndf = self.f.GetChisquare() / self.f.GetNDF()
                return list(zip(list(buf), list(buf_e))), chi2ndf, success


class SinglesFitter(Fitter):
    def __init__(self, name, xmin, xmax):
        super().__init__(name, R.powgaus, xmin, xmax, 5)
        self.f.SetParLimits(4, 0.01, 0.5)


class K40Fitter(SinglesFitter):
    def __init__(self):
        super().__init__("powgaus_k40", 1.3, 1.6)

    def fit(self, hist):
        bin1, bin2 = hist.FindBin(1), hist.FindBin(1.5)
        y1, y2 = hist.GetBinContent(bin1), hist.GetBinContent(bin2)

        # a, b, N, mu, sigma
        self.f.SetParameters(y1, 0, y2 - y1 / 2.25, 1.5, 0.12)
        return super().fit(hist)


class Tl208Fitter(SinglesFitter):
    def __init__(self):
        super().__init__("powgaus_tl208", 2.5, 2.9)

    def fit(self, hist):
        bin1, bin2 = hist.FindBin(2.3), hist.FindBin(2.8)
        y1, y2 = hist.GetBinContent(bin1), hist.GetBinContent(bin2)

        # a, b, N, mu, sigma
        self.f.SetParameters(y1 * 5.29, 0, y2 - y1 * 5.29 / 7.84, 2.8, 0.12)
        return super().fit(hist)


class C12Fitter(SinglesFitter):
    def __init__(self):
        super().__init__('powgaus_c12', 3.75, 4.15)

    def fit(self, hist):
        bin1, bin2 = hist.FindBin(3.75), hist.FindBin(4.15)
        y1, y2 = hist.GetBinContent(bin1), hist.GetBinContent(bin2)

        self.f.SetParameters(y1, 0, y2, 4, 0.15)
        self.f.FixParameter(0, 0)
        self.f.FixParameter(1, 0)
        return super().fit(hist)


class NHFitter(Fitter):
    def __init__(self):
        super().__init__("dybf", R.dybf, 1.9, 3, 6)
        # super(NHFitter, self).__init__("dybf", R.dybf, 1.8, 2.6, 6)

    def fit(self, hist):
        max_val = hist.GetMaximum()

        self.f.SetParLimits(0, 0, max_val)
        self.f.SetParLimits(1, 0, max_val)
        self.f.SetParLimits(2, 2, 2.8)
        self.f.SetParLimits(3, 0.1, 0.25)
        self.f.SetParLimits(4, 0, 2)
        self.f.SetParLimits(5, 0, 0.2 * max_val)

        # N1, N2, mu, sigma, lambda, a
        self.f.SetParameters(0.35 * 0.9 * max_val, 0.35 * 0.1 * max_val,
                             2.3, 0.14, 0.1, 0)
        return super().fit(hist)


class BaseDybNGdFitter(Fitter):
    def __init__(self, funcname, func):
        super().__init__(funcname, func, 7, 10, 6)

    def fit(self, hist):
        max_val = hist.GetMaximum()

        self.f.SetParLimits(0, 0, max_val)
        self.f.SetParLimits(1, 0, max_val)
        self.f.SetParLimits(2, 7, 9.1)
        self.f.SetParLimits(3, 0.1, 1.2)
        self.f.SetParLimits(4, 0, 2)
        self.f.SetParLimits(5, 0, 0.2 * max_val)  # WTF?

        self.f.SetParameters(0.35 * 0.9 * max_val, 0.35 * 0.1 * max_val,
                             8, 0.6, 0.1, 0)
        return super().fit(hist)


class MyDybfNGdFitter(BaseDybNGdFitter):
    def __init__(self):
        super().__init__("mydybf", R.mydybf)


class DybfNGdFitter(BaseDybNGdFitter):
    def __init__(self):
        super().__init__("dybf", R.dybf)


# XXX try without exp, like Jianrun
class BaseDoubCrysNGdFitter(Fitter):
    def __init__(self, funcname, func, extra_pars=0):
        super().__init__(funcname, func, 7, 10, 5 + extra_pars)

    def init_extra_pars(self):
        pass

    def fit(self, hist):
        max_val = hist.GetMaximum()

        self.f.SetParLimits(0, 0, max_val)
        self.f.SetParLimits(1, 0, 4)
        self.f.SetParLimits(2, 0, 15)
        self.f.SetParLimits(3, 7, 9.1)
        self.f.SetParLimits(4, 0.1, 0.6)

        self.f.SetParameters(max_val, 1, 1, 8, 0.3)
        self.init_extra_pars()
        return super().fit(hist)


class DoubCrysNGdFitter(BaseDoubCrysNGdFitter):
    def __init__(self):
        super().__init__('doubcrys', R.doubcrys)


class DoubCrysPlusExpNGdFitter(BaseDoubCrysNGdFitter):
    def __init__(self):
        super().__init__('dcbfPlusExp', R.dcbfPlusExp,
                         extra_pars=2)

    def init_extra_pars(self):
        self.f.SetParLimits(5, 0, 100)
        self.f.SetParLimits(6, -100, 0)

        self.f.SetParameter(5, 1)
        self.f.SetParameter(6, -1)


# class NGdFitter(Fitter):
#     def __init__(self):
#         # super(NGdFitter, self).__init__("dcbfPlusExp",
#         #                                 R.dcbfPlusExp, 7, 10.4, 7)
#         # super(NGdFitter, self).__init__("doubcrys",
#         #                                 R.doubcrys, 7, 10.4, 7)
#         super().__init__("doubcrys", R.doubcrys, 7, 9, 7)

#     def fit(self, hist):
#         max_val = hist.GetMaximum()

#         self.f.SetParLimits(0, 0, max_val)
#         self.f.SetParLimits(1, 0, 4)
#         self.f.SetParLimits(2, 0, 15)
#         self.f.SetParLimits(3, 7, 9.1)
#         self.f.SetParLimits(4, 0.1, 0.6)
#         self.f.SetParLimits(5, 0, 100)
#         self.f.SetParLimits(6, -100, 0)

#         self.f.SetParameters(max_val, 1, 1, 8, 0.3, 1, -1)
#         return super().fit(hist)
