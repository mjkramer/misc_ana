#pragma once

#include <TROOT.h>

#include <string>
#include <tuple>
#include <vector>

enum class Phase { k6AD = 1, k8AD, k7AD };

enum class Site { EH1 = 1, EH2, EH3 };

enum class Det { AD1 = 1, AD2, AD3, AD4, IWS, OWS };

constexpr size_t MAXDET = size_t(Det::OWS) + 1;

inline size_t idx_of(Det d)
{
  return size_t(d) - 1;
}

// So that code can determine # of ADs, etc.
extern Site gSite;
extern Phase gPhase;

namespace util {

std::vector<Det> ADsFor(Site site, Phase phase);
std::vector<size_t> iADsFor(Site site, Phase phase);

std::tuple<UInt_t, UShort_t> runAndFile(const std::string& path);

std::vector<std::string> readlines(const char* listfile);

} // namespace util
