#include "EventReader.hh"
#include "FlasherRecov.hh"
#include "Misc.hh"
#include "MuonAlg.hh"
#include "TrigTypeCut.hh"

#include <TError.h>

#include <iostream>

// So that code can determine # of ADs, etc.
Site gSite;
Phase gPhase;

void flasher_recov(const char* inFile, const char* outFile)
{
  Pipeline p;

  p.makeOutFile(outFile);

  p.makeAlg<EventReader>();
  p.makeAlg<TrigTypeCut>();
  p.makeAlg<MuonAlg>();
  p.makeAlg<FlasherRecov>();

  p.process({inFile});
}

int main(int argc, char** argv)
{
  gErrorIgnoreLevel = kError;  // suppress warnings of missing NuWa dictionaries

  if (argc != 4 + 1) {
    std::cerr << "Usage: " << argv[0] << "infile outfile site phase\n";
    return 1;
  }

  const auto inFile = argv[1];
  const auto outFile = argv[2];
  gSite = Site(std::stoul(argv[3]));
  gPhase = Phase(std::stoul(argv[4]));

  flasher_recov(inFile, outFile);

  return 0;
}
