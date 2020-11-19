#include "Sequencer.hh"
#include "Util.hh"

#include <algorithm>
#include <vector>

void run_sequencers(const std::vector<ISequencer*>& seqs,
                    float runtime_s)
{
  const int n_seq = seqs.size();
  bool done[n_seq];
  std::fill(done, done + n_seq, false);
  int remaining = n_seq;

  TTimeStamp tEnd(0, 0);
  shift_timestamp(tEnd, runtime_s);

  while (remaining > 0) {
    for (int iseq = 0; iseq < n_seq; ++iseq) {
      if (done[iseq])
        continue;
      TTimeStamp t = seqs[iseq]->next();
      if (t > tEnd) {
        done[iseq] = true;
        --remaining;
      }
    }
  }
}
