/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_REFPTR_HH
#define MOTOR_MINITL_INL_REFPTR_HH
#pragma once

#include <motor/minitl/refptr.hh>

#include <motor/minitl/features.hh>
#include <motor/minitl/format.hh>

namespace minitl {

template < typename T >
void ref< T >::swap(ref< T >& other)
{
    T* tmp_ptr  = other.operator->();
    other.m_ptr = m_ptr;
    m_ptr       = tmp_ptr;
}

template < typename T >
ref< T >::ref(T* value) : m_ptr(value)
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref(T* value, allocator& deleter) : m_ptr(value)
{
    motor_assert(value->pointer::m_allocator == 0,
        "value already has a deleter; being refcounting multiple times?");
    value->pointer::m_allocator = &deleter;
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref() : m_ptr(0)
{
}

template < typename T >
ref< T >::ref(const ref& other) : m_ptr(other.operator->())
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
template < typename U >
ref< T >::ref(const ref< U >& other) : m_ptr(check_is_a< T >(other.operator->()))
{
    if(m_ptr) m_ptr->addref();
}

template < typename T >
ref< T >::ref(ref&& other) noexcept : m_ptr(other.operator->())
{
    other.m_ptr = nullptr;
}

template < typename T >
template < typename U >
ref< T >::ref(ref< U >&& other) noexcept : m_ptr(check_is_a< T >(other.operator->()))
{
    other.m_ptr = nullptr;
}

template < typename T >
template < typename U >
ref< T >::ref(scoped< U >&& other) noexcept : m_ptr(check_is_a< T >(other.operator->()))
{
    if(m_ptr) m_ptr->addref();
    other.m_ptr = nullptr;
}

template < typename T >
ref< T >& ref< T >::operator=(const ref< T >& other)
{
    if(m_ptr == other.m_ptr) return *this;
    ref(other).swap(*this);
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(const ref< U >& other)
{
    if(m_ptr == other.m_ptr) return *this;
    ref(other).swap(*this);
    return *this;
}

template < typename T >
ref< T >& ref< T >::operator=(ref< T >&& other) noexcept
{
    if(m_ptr) m_ptr->decref();
    m_ptr       = other.m_ptr;
    other.m_ptr = nullptr;
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(ref< U >&& other) noexcept
{
    if(m_ptr) m_ptr->decref();
    m_ptr       = check_is_a< T >(other.m_ptr);
    other.m_ptr = nullptr;
    return *this;
}

template < typename T >
ref< T >::~ref()
{
    if(m_ptr) m_ptr->decref();
}

template < typename T >
T* ref< T >::operator->() const
{
    return static_cast< T* >(m_ptr);
}

template < typename T >
ref< T >::operator const void*() const
{
    return m_ptr;
}

template < typename T >
bool ref< T >::operator!() const
{
    return m_ptr == 0;
}

template < typename T >
T& ref< T >::operator*()
{
    return *static_cast< T* >(m_ptr);
}

template < typename T >
void ref< T >::clear()
{
    if(m_ptr) m_ptr->decref();
    m_ptr = 0;
}

template < typename T, typename U >
bool operator==(const ref< T >& ref1, const ref< U >& ref2)
{
    return ref1.operator->() == ref2.operator->();
}

template < typename T, typename U >
bool operator!=(const ref< T >& ref1, const ref< U >& ref2)
{
    return ref1.operator->() != ref2.operator->();
}

}  // namespace minitl

#endif
