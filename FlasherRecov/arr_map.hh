#pragma once

#include <cstddef>              // size_t
#include <type_traits>

namespace util {

// Quick hack: An array that we can access with non-integral index (e.g. a Det).
// This just avoids the ugliness of explicitly casting the index to size_t. If T
// is a pointer, we zero-initialize the array. Other the elements get
// default-initialized.
template <class T, size_t N, class Enable = void>
class arr_map;

template <class T, size_t N>
class arr_map<T, N, std::enable_if_t<not std::is_pointer_v<T>>> {
public:
  template <class I>
  T& operator[](I i)
  {
    return vals[size_t(i)];
  }

private:
  T vals[N];
};

template <class T, size_t N>
class arr_map<T, N, std::enable_if_t<std::is_pointer_v<T>>> {
public:
  template <class I>
  T& operator[](I i)
  {
    return vals[size_t(i)];
  }

private:
  T vals[N] = {0};
};

} // namespace util
