/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_SCOPEDPTR_HH
#define MOTOR_MINITL_INL_SCOPEDPTR_HH
#pragma once

#include <motor/minitl/scopedptr.hh>

#include <motor/minitl/features.hh>
#if MOTOR_ENABLE_ASSERT
#    include <typeinfo>
#endif

namespace minitl {

template < typename T >
scoped< T >::scoped(T* value, allocator& allocator) : m_ptr(value)
{
    motor_assert_format(
        value->pointer::m_allocator == 0,
        "value of type {0} already has a deleter; being refcounting multiple times?",
        typeid(T).name());
    value->pointer::m_allocator = &allocator;
}

template < typename T >
scoped< T >::scoped() : m_ptr(0)
{
}

template < typename T >
scoped< T >::~scoped()
{
    if(m_ptr) m_ptr->checked_delete();
}

template < typename T >
scoped< T >::scoped(scoped&& other) noexcept : m_ptr(other.m_ptr)
{
    other.m_ptr = 0;
}

template < typename T >
template < typename U >
scoped< T >::scoped(scoped< U >&& other) : m_ptr(other.m_ptr)
{
    other.m_ptr = 0;
}

template < typename T >
template < typename U >
void scoped< T >::reset(scoped< U >&& other)
{
    if(m_ptr != other.m_ptr)
    {
        if(m_ptr)
        {
            m_ptr->checked_delete();
        }
        m_ptr       = other.m_ptr;
        other.m_ptr = 0;
    }
}

template < typename T >
T* scoped< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
scoped< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool scoped< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& scoped< T >::operator*()
{
    return *m_ptr;
}

template < typename T, typename U >
bool operator==(const scoped< T >& ref1, const scoped< U >& ref2)
{
    return ref1.operator->() == ref2.operator->();
}

template < typename T, typename U >
bool operator!=(const scoped< T >& ref1, const scoped< U >& ref2)
{
    return ref1.operator->() != ref2.operator->();
}

}  // namespace minitl

#endif
