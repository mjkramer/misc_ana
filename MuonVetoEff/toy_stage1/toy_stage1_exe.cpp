#include "AdGen.hh"
#include "MuonGen.hh"

#include <TFile.h>
#include <TH1F.h>
#include <TTree.h>

const float RUNTIME_S = 1e5;

int main()
{
  TFile outFile("toy_stage1.root", "RECREATE");

  TTree muonTree("muons", "muons");
  MuonSink muonSink(&muonTree);
  Sequencer muonSeq(&muonSink);

  MuonSource wpSource(5, 180, 15);
  MuonSource adSource(1, 20, 5e3);
  MuonSource shSource(1, 0.1, 5e5);

  muonSeq.addSources({&wpSource, &adSource, &shSource});

  TTree adTree("physics_AD1", "physics_AD1");
  AdSink adSink(&adTree);
  Sequencer adSeq(&adSink);

  SingleSource plsSource(30, 2);
  SingleSource dlsSource(1, 9);
  IbdSource ibdSource(0.1);

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
