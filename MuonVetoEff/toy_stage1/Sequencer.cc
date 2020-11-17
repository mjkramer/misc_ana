#include "Sequencer.hh"

#include <algorithm>
#include <vector>

void run_sequencers(std::vector<ISequencer*> seqs,
                    float runtime_s)
{
  const int n_seq = seqs.size();
  bool done[n_seq];
  std::fill(done, done + n_seq, false);
  int remaining = n_seq;

  const Time tEnd = Time().shifted_us(1e6 * runtime_s);

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
}
