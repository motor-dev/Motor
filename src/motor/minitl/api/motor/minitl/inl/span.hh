/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_SPAN_HH
#define MOTOR_MINITL_INL_SPAN_HH
#pragma once

#include <motor/minitl/span.hh>

#include <motor/minitl/assert.hh>

namespace minitl {

template < typename T >
span< T >::span(T* begin, T* end) : m_begin(begin)
                                  , m_end(end)
{
}

template < typename T >
span< T >::span(initializer_list< T > init_list)
    : m_begin(init_list.begin())
    , m_end(init_list.end())
{
}

template < typename T >
typename span< T >::iterator span< T >::begin()
{
    return m_begin;
}

template < typename T >
typename span< T >::iterator span< T >::end()
{
    return m_end;
}
template < typename T >
typename span< T >::const_iterator span< T >::begin() const
{
    return m_begin;
}

template < typename T >
typename span< T >::const_iterator span< T >::end() const
{
    return m_end;
}

template < typename T >
T& span< T >::operator[](u32 index)
{
    motor_assert_format(index < size(), "index {0} out of bounds: view size is {1}", index, size());
    return m_begin[index];
}

template < typename T >
const T& span< T >::operator[](u32 index) const
{
    motor_assert_format(index < size(), "index {0} out of bounds: view size is {1}", index, size());
    return m_begin[index];
}

template < typename T >
u32 span< T >::size() const
{
    return u32(m_end - m_begin);
}

template < typename T >
T& span< T >::first()
{
    return *m_begin;
}

template < typename T >
T& span< T >::last()
{
    return *(m_end - 1);
}

template < typename T >
const T& span< T >::first() const
{
    return *m_begin;
}

template < typename T >
const T& span< T >::last() const
{
    return *(m_end - 1);
}

}  // namespace minitl

#endif
