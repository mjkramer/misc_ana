#include "LivetimeWriter.hh"

#include <TH1F.h>
#include <TParameter.h>

void LivetimeWriter::finalize(Pipeline& pipe)
{
  TFile* inFile = pipe.inFile();

  auto h_livetime = (TH1F*) inFile->Get("h_livetime");
  float livetime = h_livetime->GetBinContent(1);

  auto p_livetime = new TParameter<float>("livetime", livetime);
  pipe.getOutFile()->cd();
  p_livetime->Write();
}
