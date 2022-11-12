/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
struct less
{
    bool operator()(const T& a, const T& b) const
    {
        return a < b;
    }
};

template < typename ITERATOR, typename FUNCTOR >
void for_each(ITERATOR first, ITERATOR last, FUNCTOR f);

template < typename ITERATOR, typename T >
void fill(ITERATOR first, ITERATOR last, const T& value);

template < typename ITERATOR, typename PREDICATE >
ITERATOR partition(ITERATOR first, ITERATOR last, PREDICATE p);

template < typename ITERATOR, typename COMPARE >
void sort(ITERATOR first, ITERATOR last, COMPARE f);

template < typename ITERATOR, typename T >
ITERATOR find(const T& t, ITERATOR begin, ITERATOR end);

}  // namespace minitl

#include <motor/minitl/inl/algorithm.inl>
