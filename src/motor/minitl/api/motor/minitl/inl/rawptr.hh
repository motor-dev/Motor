/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_RAWPTR_HH
#define MOTOR_MINITL_INL_RAWPTR_HH
#pragma once

#include <motor/minitl/rawptr.hh>

namespace minitl {

template < typename T >
T* raw< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
raw< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool raw< T >::operator!() const
{
    return m_ptr == nullptr;
}

template < typename T >
T& raw< T >::operator*()
{
    return *m_ptr;
}

template < typename T >
const T& raw< T >::operator*() const
{
    return *m_ptr;
}

template < typename T >
raw< T > raw< T >::null()
{
    raw< T > result = {nullptr};
    return result;
}

}  // namespace minitl

#endif
