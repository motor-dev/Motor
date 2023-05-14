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
void sort(ITERATOR first, ITERATOR last, COMPARE s);

template < typename ITERATOR, typename T >
ITERATOR find(const T& t, ITERATOR begin, ITERATOR end);

}  // namespace minitl

#include <motor/minitl/iterator.hh>
#include <motor/minitl/swap.hh>

namespace minitl {

namespace details {

template < typename ITERATOR, typename COMPARE >
struct sort_predicate
{
    ITERATOR m_iterator;
    COMPARE  m_compare;
    explicit sort_predicate(ITERATOR it) : m_iterator(it)
    {
    }
    bool operator()(const ITERATOR& r)
    {
        return m_compare(*m_iterator, *r);
    }
};

}  // namespace details

template < typename ITERATOR, typename FUNCTOR >
void for_each(ITERATOR first, ITERATOR last, FUNCTOR f)
{
    for(; first != last; ++first)
        f(*first);
}

template < typename ITERATOR, typename T >
void fill(ITERATOR first, ITERATOR last, const T& value)
{
    for(; first != last; ++first)
        *first = value;
}

template < typename ITERATOR, typename PREDICATE >
ITERATOR partition(ITERATOR first, ITERATOR last, PREDICATE p)
{
    ITERATOR middle = first;
    for(; first != last; ++first)
    {
        if(!p(first))
        {
            minitl::swap(*first, *middle);
            ++middle;
        }
    }
    return middle;
}

template < typename ITERATOR, typename COMPARE >
void sort(ITERATOR first, ITERATOR last, COMPARE s)
{
    minitl::difference_t d = distance(first, last);
    if(d > 1)
    {
        ITERATOR reallast = last - 1;
        ITERATOR t        = first + d / 2;
        swap(*t, *reallast);
        t = partition(first, reallast, details::sort_predicate< ITERATOR, COMPARE >(reallast));
        swap(*t, *reallast);
        sort(first, t, s);
        sort(t, last, s);
    }
}

template < typename ITERATOR, typename T >
ITERATOR find(const T& t, ITERATOR begin, ITERATOR end)
{
    for(ITERATOR it = begin; it != end; ++it)
    {
        if(*it == t) return it;
    }
    return end;
}

}  // namespace minitl
