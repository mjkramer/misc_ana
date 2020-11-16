#pragma once

#include <TTree.h>

enum class IOMode { IN, OUT };

template <class EventT>
class TreeWrapper {
public:
  using EventType = EventT;
  TreeWrapper(TTree* tree, IOMode mode);
  virtual void init() = 0;
  EventT* operator->() const;
  TreeWrapper<EventT>& operator=(const EventT& rhs);
  TTree* tree();

private:
  EventT data_;
  TTree* tree_;
  IOMode mode_;
};

template <typename T>
void make_branch(TTree* tree, IOMode mode, const char* name,
                 T* ptr)
{
  if (mode == IOMode::IN) {
    tree->SetBranchStatus(name, true);
    tree->SetBranchAddress(name, ptr);
  } else {
    tree->Branch(name, ptr);
  }
}

#define NEW_BR(name) make_branch(tree_, mode_, #name, &data_.name)

template <typename EventT>
TreeWrapper<EventT>::TreeWrapper(TTree* tree, IOMode mode) :
  tree_(tree), mode_(mode)
{
  if (mode == IOMode::IN) {
    tree_->SetBranchStatus("*", false);
  }

  init();
}

template <typename EventT>
TTree* TreeWrapper<EventT>::tree()
{
  return tree_;
}

template <typename EventT>
EventT* TreeWrapper<EventT>::operator->() const
{
  return &data_;
}

template <typename EventT>
TreeWrapper<EventT>& TreeWrapper<EventT>::operator=(const EventT& rhs)
{
  data_ = rhs;
}
