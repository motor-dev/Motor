/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_WEAKPTR_HH
#define MOTOR_MINITL_INL_WEAKPTR_HH
#pragma once

#include <motor/minitl/weakptr.hh>

#include <motor/minitl/cast.hh>
#include <motor/minitl/hash.hh>

namespace minitl {

template < typename T >
void weak< T >::swap(weak& other)
{
    minitl::swap(m_ptr, other.m_ptr);
}

template < typename T >
weak< T >::weak() : m_ptr(0)
{
}

template < typename T >
weak< T >::weak(T* p) : m_ptr(p)
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(const ref< U >& other) : m_ptr(motor_implicit_cast< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(const scoped< U >& other) : m_ptr(motor_implicit_cast< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
weak< T >::weak(const weak& other) : m_ptr(other.operator->())
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(const weak< U >& other) : m_ptr(motor_implicit_cast< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
weak< T >::~weak()
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->dec_weak();
#endif
}

template < typename T >
weak< T >& weak< T >::operator=(const weak& other)
{
    if(this != &other)
    {
        weak(other).swap(*this);
    }
    return *this;
}

template < typename T >
template < typename U >
weak< T >& weak< T >::operator=(const weak< U >& other)
{
    weak(other).swap(*this);
    return *this;
}

template < typename T >
template < typename U >
weak< T >& weak< T >::operator=(U* other)
{
    weak(other).swap(*this);
    return *this;
}

template < typename T >
T* weak< T >::operator->() const
{
    return static_cast< T* >(m_ptr);
}

template < typename T >
weak< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool weak< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& weak< T >::operator*()
{
    return *static_cast< T* >(m_ptr);
}

template < typename T >
void weak< T >::clear()
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->dec_weak();
#endif
    m_ptr = 0;
}

template < typename U, typename T >
inline weak< U > motor_checked_cast(const weak< T >& value)
{
    motor_assert(!value || dynamic_cast< U* >(value.operator->()), "invalid cast");
    return weak< U >(static_cast< U* >(value.operator->()));
}

}  // namespace minitl

#endif
