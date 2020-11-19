#pragma once

#include "NewIO.hh"

#include <TRandom3.h>
#include <TTimeStamp.h>

#include <cstdint>
#include <tuple>
#include <vector>

template <class EventT>
struct IEventSource {
  virtual std::tuple<TTimeStamp, EventT> next() = 0;
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
  virtual TTimeStamp next() = 0;
};

template <class EventT>
class Sequencer : virtual public ISequencer {
public:
  Sequencer(IEventSink<EventT>* sink);
  void addSources(std::vector<IEventSource<EventT>*> sources);
  TTimeStamp next() override;

private:
  IEventSink<EventT>* sink_;
  std::vector<IEventSource<EventT>*> sources_;
  std::vector<std::tuple<TTimeStamp, EventT>> lastEvents_;

  void prime();
};

template <class EventT>
Sequencer<EventT>::Sequencer(IEventSink<EventT>* sink) :
  sink_(sink) {}

template <class EventT>
void Sequencer<EventT>::addSources(std::vector<IEventSource<EventT>*> sources)
{
  for (auto source : sources)
    sources_.push_back(source);
}

template <class EventT>
TTimeStamp Sequencer<EventT>::next()
{
  if (lastEvents_.size() == 0)
    prime();

  TTimeStamp earliestTime {INT32_MAX, 0};
  int iEarliest;

  for (int i = 0; i < sources_.size(); ++i) {
    auto [time, _event] = lastEvents_[i];

    if (time < earliestTime) {
      earliestTime = time;
      iEarliest = i;
    }
  }

  auto [time, event] = lastEvents_[iEarliest];
  sink_->sink(event);

  lastEvents_[iEarliest] = sources_[iEarliest]->next();

  return time;
}

template <class EventT>
void Sequencer<EventT>::prime()
{
  for (auto source : sources_)
    lastEvents_.push_back(source->next());
}

void run_sequencers(std::vector<ISequencer*> seqs,
                    float runtime_s = 1e5);
