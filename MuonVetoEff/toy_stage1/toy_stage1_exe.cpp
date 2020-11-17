#include "AdGen.hh"
#include "MuonGen.hh"

#include <TFile.h>
#include <TH1F.h>
#include <TTree.h>

const float RUNTIME_SEC = 1e5;

int main()
{
  TFile outFile("toy_stage1.root", "RECREATE");

  TTree muonTree("muons", "muons");
  MuonSink muonSink(&muonTree);
  Sequencer muonSeq(muonSink);

  MuonSource wpSource(5, 180, 15);
  muonSeq.addSource(wpSource);
  MuonSource adSource(1, 20, 5e3);
  muonSeq.addSource(adSource);
  MuonSource shSource(1, 0.1, 5e5);
  muonSeq.addSource(shSource);

  TTree adTree("physics_AD1", "physics_AD1");
  AdSink adSink(&adTree);
  Sequencer adSeq(adSink);

  SingleSource plsSource(30, 2);
  adSeq.addSource(plsSource);
  SingleSource dlsSource(1, 9);
  adSeq.addSource(dlsSource);

  ISequencer* seqs[] = {&muonSeq, &adSeq};
  constexpr int n_seq = sizeof(seqs)/sizeof(seqs[0]);
  bool done[n_seq] = {0};
  int remaining = n_seq;
  const Time tEnd = Time().shifted_us(1e6 * RUNTIME_SEC);

  while (remaining > 0) {
    for (int iseq = 0; iseq < n_seq; ++iseq) {
      if (done[iseq])
        continue;
      Time t = seqs[iseq]->next();
      if (t > tEnd) {
        done[iseq] = true;
        --remaining;
      }
    }
  }

  muonTree.Write();
  adTree.Write();

  TH1F h_livetime("h_livetime", "Livetime (s)", 1, 0, 1);
  h_livetime.SetBinContent(1, RUNTIME_SEC);
  h_livetime.Write();

  return 0;
}
