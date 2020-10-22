#include <iostream>

#include "LivetimeWriter.hh"
#include "MuonReader.hh"
#include "MuonCondenser.hh"

void condense(const char* inFile, const char* outFile)
{
  Pipeline p;

  p.makeOutFile(outFile);

  p.makeAlg<MuonReader>();
  p.makeAlg<MuonCondenser>();
  p.makeAlg<LivetimeWriter>();

  p.process({inFile});
}

int main(int argc, char** argv)
{
  if (argc != 2 + 1) {
    std::cerr << "Usage: " << argv[0] << " inFile outFile" << std::endl;
    return 1;
  }

  const auto inFile = argv[1];
  const auto outFile = argv[2];

  condense(inFile, outFile);
}
