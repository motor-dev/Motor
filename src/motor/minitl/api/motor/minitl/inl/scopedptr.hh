/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_SCOPEDPTR_HH
#define MOTOR_MINITL_INL_SCOPEDPTR_HH
#pragma once

#include <motor/minitl/scopedptr.hh>

#include <motor/minitl/features.hh>

namespace minitl {

template < typename T >
scoped< T >::scoped(details::scoped_payload* payload, T* value) : m_payload(payload)
                                                                , m_ptr(value)
{
}

template < typename T >
scoped< T >::scoped() : m_payload(nullptr)
                      , m_ptr(nullptr)
{
}

template < typename T >
scoped< T >::~scoped()
{
    if(m_payload)
    {
        allocator& arena = m_payload->arena;
        m_payload->~scoped_payload();
        arena.free(m_payload);
    }
}

template < typename T >
scoped< T >::scoped(scoped&& other) noexcept : m_payload(other.m_payload)
                                             , m_ptr(other.m_ptr)
{
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
}

template < typename T >
scoped< T >& scoped< T >::operator=(scoped&& other) noexcept
{
    if(m_payload)
    {
        allocator& arena = m_payload->arena;
        m_payload->~scoped_payload();
        arena.free(m_payload);
    }
    m_payload       = other.m_payload;
    m_ptr           = other.m_ptr;
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
    return *this;
}

template < typename T >
template < typename U >
scoped< T >::scoped(scoped< U >&& other)
    : m_payload(other.m_payload)
    , m_ptr(motor_implicit_cast< T >(other.m_ptr))
{
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
}

template < typename T >
template < typename U >
scoped< T >& scoped< T >::operator=(scoped< U >&& other) noexcept
{
    if(m_payload)
    {
        allocator& arena = m_payload->arena;
        m_payload->~scoped_payload();
        arena.free(m_payload);
    }
    m_payload       = other.m_payload;
    m_ptr           = motor_implicit_cast< T >(other.m_ptr);
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
    return *this;
}

template < typename T >
T* scoped< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
scoped< T >::operator const void*() const
{
    return static_cast< const void* >(m_ptr);
}

template < typename T >
bool scoped< T >::operator!() const
{
    return m_ptr == nullptr;
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

template < typename U, typename T >
inline scoped< U > motor_checked_cast(scoped< T >&& value)
{
    motor_assert(!value || dynamic_cast< U* >(value.operator->()), "invalid cast");
    details::scoped_payload* payload = value.m_payload;
    U*                       ptr     = static_cast< U* >(value.m_ptr);
    value.m_payload                  = nullptr;
    value.m_ptr                      = nullptr;
    return scoped< U >(payload, ptr);
}

template < typename U, typename T >
inline weak< U > motor_checked_cast(const scoped< T >& value)
{
    motor_assert(!value || dynamic_cast< U* >(value.operator->()), "invalid cast");
    return weak< U >(static_cast< U* >(value.operator->()));
}

}  // namespace minitl

#endif
