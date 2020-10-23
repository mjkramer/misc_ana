#include "LivetimeWriter.hh"

#include <TH1F.h>

void LivetimeWriter::finalize(Pipeline& pipe)
{
  auto h_livetime = (TH1F*) pipe.inFile()->Get("h_livetime");
  pipe.getOutFile()->cd();
  h_livetime->Write();
}
