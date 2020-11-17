#pragma once

#include "NewIO.hh"

#include "Framework/Util.hh"

#include <TRandom3.h>

#include <cstdint>
#include <map>
#include <tuple>
#include <vector>

template <class EventT>
struct IEventSource {
  virtual std::tuple<Time, EventT> next() = 0;
};

template <class EventT>
class RanEventSource : virtual public IEventSource<EventT> {
public:
  RanEventSource();

protected:
  TRandom3& ran();

private:
  TRandom3 ran_;
};

template <class EventT>
RanEventSource<EventT>::RanEventSource()
{
  ran_.SetSeed();
}

template <class EventT>
TRandom3& RanEventSource<EventT>::ran()
{
  return ran_;
}

template <class EventT>
struct IEventSink {
  virtual void sink(EventT event) = 0;
};

template <class TreeWrapperT>
class TreeSink : virtual public IEventSink<typename TreeWrapperT::EventType> {
public:
  TreeSink(TTree* tree);
  ~TreeSink();
  void sink(typename TreeWrapperT::EventType event) override;
  virtual void prep(typename TreeWrapperT::EventType& event) { };

private:
  TreeWrapperT wrapper_;
};

template <class TreeWrapperT>
TreeSink<TreeWrapperT>::TreeSink(TTree* tree) :
  wrapper_(tree, IOMode::OUT) {}

template <class TreeWrapperT>
TreeSink<TreeWrapperT>::~TreeSink()
{
  wrapper_.tree()->Write();
}

template <class TreeWrapperT>
void TreeSink<TreeWrapperT>::sink(typename TreeWrapperT::EventType event)
{
  prep(event);
  wrapper_.set(event);
  wrapper_.tree()->Fill();
}

struct ISequencer {
  virtual Time next() = 0;
};

template <class EventT>
class Sequencer : virtual public ISequencer {
public:
  Sequencer(IEventSink<EventT>& sink);
  void addSource(IEventSource<EventT>& source);
  Time next() override;

private:
  IEventSink<EventT>& sink_;
  std::vector<IEventSource<EventT>*> sources_;
  std::map<IEventSource<EventT>*,
           std::tuple<Time, EventT>> lastEvents_;

  void prime();
};

template <class EventT>
Sequencer<EventT>::Sequencer(IEventSink<EventT>& sink) :
  sink_(sink) {}

template <class EventT>
void Sequencer<EventT>::addSource(IEventSource<EventT>& source)
{
  sources_.push_back(&source);
}

template <class EventT>
Time Sequencer<EventT>::next()
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
  sink_.sink(event);

  lastEvents_[earliestSource] = earliestSource->next();

  return time;
}

template <class EventT>
void Sequencer<EventT>::prime()
{
  for (auto source : sources_) {
    lastEvents_[source] = source->next();
  }
}
