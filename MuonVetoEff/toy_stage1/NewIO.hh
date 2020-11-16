#pragma once

#include <TTree.h>

enum class IOMode { IN, OUT };

template <class TreeData>
class TreeWrapper {
public:
  TreeWrapper(TTree* tree, IOMode mode);
  virtual void init() = 0;
  TreeData* operator->() const;
  TreeWrapper<TreeData>& operator=(const TreeData& rhs);
  TTree* tree();

private:
  TreeData data_;
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

template <typename TreeData>
TreeWrapper<TreeData>::TreeWrapper(TTree* tree, IOMode mode) :
  tree_(tree), mode_(mode)
{
  if (mode == IOMode::IN) {
    tree_->SetBranchStatus("*", false);
  }

  init();
}

template <typename TreeData>
TTree* TreeWrapper<TreeData>::tree()
{
  return tree_;
}

template <typename TreeData>
TreeData* TreeWrapper<TreeData>::operator->() const
{
  return &data_;
}

template <typename TreeData>
TreeWrapper<TreeData>& TreeWrapper<TreeData>::operator=(const TreeData& rhs)
{
  data_ = rhs;
}
