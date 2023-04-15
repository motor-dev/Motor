/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/algorithm.hh>
#include <motor/minitl/array.hh>
#include <motor/minitl/assert.hh>
#include <motor/minitl/cast.hh>

namespace minitl {

template < typename T >
array< T >::array(Allocator& allocator, u32 size) : m_array(allocator, size)
{
    for(u32 i = 0; i < size; ++i)
    {
        new((void*)&m_array[i]) T;
    }
}

template < typename T >
template < typename ITERATOR >
array< T >::array(Allocator& allocator, ITERATOR begin, ITERATOR end)
    : m_array(allocator, distance(begin, end))
{
    for(int i = 0; begin != end; ++begin, ++i)
    {
        new((void*)&m_array[i]) T(*begin);
    }
}

template < typename T >
array< T >::array(const array< T >& other) : m_array(other.m_array.arena(), other.size())
{
    for(u32 i = 0; i < size(); ++i)
    {
        new((void*)&m_array[i]) T(other[i]);
    }
}

template < typename T >
array< T >::array(array< T >&& other) noexcept : m_array(move(other.m_array))
{
}

template < typename T >
array< T >::~array()
{
    for(u64 i = m_array.count(); i > 0; --i)
    {
        m_array[i - 1].~T();
    }
}

template < typename T >
typename array< T >::iterator array< T >::begin()
{
    return &m_array[0];
}

template < typename T >
typename array< T >::iterator array< T >::end()
{
    return &m_array[m_array.count()];
}

template < typename T >
typename array< T >::const_iterator array< T >::begin() const
{
    return &m_array[0];
}

template < typename T >
typename array< T >::const_iterator array< T >::end() const
{
    return &m_array[m_array.count()];
}

template < typename T >
T& array< T >::operator[](u32 index)
{
    motor_assert_format(index < m_array.count(), "index {0} out of bounds: array size is {1}",
                        index, m_array.count());
    return m_array[index];
}

template < typename T >
const T& array< T >::operator[](u32 index) const
{
    motor_assert_format(index < m_array.count(), "index {0} out of bounds: array size is {1}",
                        index, m_array.count());
    return m_array[index];
}

template < typename T >
u32 array< T >::size() const
{
    return motor_checked_numcast< u32 >(m_array.count());
}

template < typename T >
void array< T >::swap(array< T >& other)
{
    m_array.swap(other.m_array);
}

template < typename T >
T& array< T >::first()
{
    motor_assert(m_array.count() != 0, "first() called on empty array");
    return m_array[0];
}

template < typename T >
const T& array< T >::first() const
{
    motor_assert(m_array.count() != 0, "first() called on empty array");
    return m_array[0];
}

template < typename T >
T& array< T >::last()
{
    motor_assert(m_array.count() != 0, "last() called on empty array");
    return m_array[m_array.count() - 1];
}

template < typename T >
const T& array< T >::last() const
{
    motor_assert(m_array.count() != 0, "last() called on empty array");
    return m_array[m_array.count() - 1];
}

}  // namespace minitl
