/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_ARRAY_HH
#define MOTOR_MINITL_INL_ARRAY_HH
#pragma once

#include <motor/minitl/array.hh>

#include <motor/minitl/assert.hh>
#include <motor/minitl/cast.hh>

namespace minitl {

template < typename T, u32 COUNT >
typename array< T, COUNT >::iterator array< T, COUNT >::begin()
{
    return &m_array[0];
}

template < typename T, u32 COUNT >
typename array< T, COUNT >::iterator array< T, COUNT >::end()
{
    return COUNT + &m_array[0];
}

template < typename T, u32 COUNT >
typename array< T, COUNT >::const_iterator array< T, COUNT >::begin() const
{
    return &m_array[0];
}

template < typename T, u32 COUNT >
typename array< T, COUNT >::const_iterator array< T, COUNT >::end() const
{
    return COUNT + &m_array[0];
}

template < typename T, u32 COUNT >
T& array< T, COUNT >::operator[](u32 index)
{
    motor_assert_format(index < COUNT, "index {0} out of bounds: array size is {1}", index, COUNT);
    return m_array[index];
}

template < typename T, u32 COUNT >
const T& array< T, COUNT >::operator[](u32 index) const
{
    motor_assert_format(index < COUNT, "index {0} out of bounds: array size is {1}", index, COUNT);
    return m_array[index];
}

template < typename T, u32 COUNT >
u32 array< T, COUNT >::size() const
{
    return COUNT;
}

template < typename T, u32 COUNT >
T& array< T, COUNT >::first()
{
    return m_array[0];
}

template < typename T, u32 COUNT >
const T& array< T, COUNT >::first() const
{
    return m_array[0];
}

template < typename T, u32 COUNT >
T& array< T, COUNT >::last()
{
    return m_array[m_array.count() - 1];
}

template < typename T, u32 COUNT >
const T& array< T, COUNT >::last() const
{
    return m_array[COUNT - 1];
}

}  // namespace minitl

#endif
