// XXX would be more realistic to include AD+WP muons

#include "AdGen.hh"
#include "MuonGen.hh"

#include "Framework/ConfigTool.hh"

#include <TFile.h>
#include <TH1F.h>
#include <TTree.h>

#include <iostream>

const float RUNTIME_S = 1e5;

int main(int argc, const char** argv)
{
  if (argc != 3) {
    std::cerr << "Usage: " << argv[0] << " [conffile] [outfile]"
              << std::endl;
    return 1;
  }

  Config config(argv[1]);
#define C(key) config.get<float>(key)

  TFile outFile(argv[2], "RECREATE");

  TTree muonTree("muons", "muons");
  MuonSink muonSink(&muonTree);
  Sequencer muonSeq(&muonSink);

  MuonSource wpSource(5, C("wpRate"), 15);
  MuonSource adSource(1, C("adRate"), 5e3);
  MuonSource shSource(1, C("shRate"), 5e5);

  muonSeq.addSources({&wpSource, &adSource, &shSource});

  TTree adTree("physics_AD1", "physics_AD1");
  AdSink adSink(&adTree);
  Sequencer adSeq(&adSink);

  SingleSource plsSource(C("plsRate"), 2);
  SingleSource dlsSource(C("dlsRate"), 9);
  IbdSource ibdSource(C("ibdRate"));

  adSeq.addSources({&plsSource, &dlsSource, &ibdSource});

  run_sequencers({&muonSeq, &adSeq},
                 RUNTIME_S);

  muonTree.Write();
  adTree.Write();

  TH1F h_livetime("h_livetime", "Livetime (s)", 1, 0, 1);
  h_livetime.SetBinContent(1, RUNTIME_S);
  h_livetime.Write();

  return 0;
}
