#pragma once

#include "Framework/Kernel.hh"

class LivetimeWriter : public Algorithm {
public:
  void finalize(Pipeline& pipe) override;
};
