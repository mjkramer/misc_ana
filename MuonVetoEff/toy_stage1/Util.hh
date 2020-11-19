#pragma once

#include <TTimeStamp.h>

inline void shift_timestamp(TTimeStamp& ts, double delta)
{
  ts.Add({time_t(delta),
          int(1e9*(delta - time_t(delta)))});
}
