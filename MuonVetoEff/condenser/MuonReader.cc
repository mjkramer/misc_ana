#include "MuonReader.hh"

void MuonTree::initBranches()
{
  BR(detector);
  BR(trigSec);
  BR(trigNanoSec);
  BR(strength);
}
