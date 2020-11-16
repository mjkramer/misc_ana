#pragma once

#include "Framework/Util.hh"

#include <cstdint>
#include <map>
#include <tuple>
#include <vector>

template <class EventT>
struct IEventSource {
  virtual std::tuple<Time, EventT> next();
};

template <class EventT>
struct IEventSink {
  virtual void sink(const std::tuple<Time, EventT> event);
};

template <class EventT>
class Sequencer {
public:
  Sequencer(IEventSink<EventT>* sink);
  void addSource(IEventSource<EventT>* source);
  void next();
  Time lastTime() const;

private:
  IEventSink<EventT>* sink_;
  std::vector<IEventSource<EventT>*> sources_;
  std::map<IEventSource<EventT>*,
           std::tuple<Time, EventT>> lastEvents_;
  Time lastTime_;

  void prime();
};

template <class EventT>
Sequencer<EventT>::Sequencer(IEventSink<EventT>* sink) :
  sink_(sink) {}

template <class EventT>
void Sequencer<EventT>::addSource(IEventSource<EventT>* source)
{
  sources_.push_back(source);
}

template <class EventT>
void Sequencer<EventT>::next()
{
  if (lastEvents_.count(sources_[0]) == 0)
    prime();

  Time earliestTime {UINT32_MAX, UINT32_MAX};
  IEventSource<EventT>* earliestSource = nullptr;

  for (auto source : sources_) {
    auto [time, _event] = lastEvents_[source];

    if (time < earliestTime) {
      earliestSource = source;
    }
  }

  auto [time, event] = lastEvents_[earliestSource];
  sink_->sink({time, event});

  lastEvents_[earliestSource] = earliestSource->next();

  lastTime_ = time;
}

template <class EventT>
Time Sequencer<EventT>::lastTime() const
{
  return lastTime_;
}

template <class EventT>
void Sequencer<EventT>::prime()
{
  for (auto source : sources_) {
    lastEvents_[source] = source->next();
  }
}
