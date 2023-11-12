/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_REFPTR_HH
#define MOTOR_MINITL_INL_REFPTR_HH
#pragma once

#include <motor/minitl/refptr.hh>

#include <motor/minitl/cast.hh>
#include <motor/minitl/features.hh>
#include <motor/minitl/format.hh>

namespace minitl {

template < typename T >
void ref< T >::swap(ref< T >& other)
{
    minitl::swap(m_payload, other.m_payload);
    minitl::swap(m_ptr, other.m_ptr);
}

template < typename T >
ref< T >::ref(details::ref_payload* payload, T* value) : m_payload(payload)
                                                       , m_ptr(value)
{
    ++m_payload->reference_count;
}

template < typename T >
ref< T >::ref() : m_payload(nullptr)
                , m_ptr(nullptr)
{
}

template < typename T >
ref< T >::ref(const ref& other) : m_payload(other.m_payload)
                                , m_ptr(other.m_ptr)
{
    if(m_payload)
    {
        ++m_payload->reference_count;
    }
}

template < typename T >
template < typename U >
ref< T >::ref(const ref< U >& other)
    : m_payload(other.m_payload)
    , m_ptr(motor_implicit_cast< T >(other.m_ptr))
{
    if(m_payload)
    {
        ++m_payload->reference_count;
    }
}

template < typename T >
ref< T >::ref(ref&& other) noexcept : m_payload(other.m_payload)
                                    , m_ptr(other.m_ptr)
{
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
}

template < typename T >
template < typename U >
ref< T >::ref(ref< U >&& other) noexcept
    : m_payload(other.m_payload)
    , m_ptr(motor_implicit_cast< T >(other.m_ptr))
{
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
}

template < typename T >
ref< T >& ref< T >::operator=(const ref< T >& other)
{
    if(this == &other) return *this;
    ref(other).swap(*this);
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(const ref< U >& other)
{
    ref(other).swap(*this);
    return *this;
}

template < typename T >
ref< T >& ref< T >::operator=(ref< T >&& other) noexcept
{
    if(m_payload && --m_payload->reference_count == 0)
    {
        allocator& a = m_payload->allocator;
        m_payload->~ref_payload();
        a.free(m_payload);
    }
    m_payload       = other.m_payload;
    m_ptr           = other.m_ptr;
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
    return *this;
}

template < typename T >
template < typename U >
ref< T >& ref< T >::operator=(ref< U >&& other) noexcept
{
    if(m_payload && --m_payload->reference_count == 0)
    {
        allocator& a = m_payload->allocator;
        m_payload->~ref_payload();
        a.free(m_payload);
    }
    m_payload       = other.m_payload;
    m_ptr           = motor_implicit_cast< T >(other.m_ptr);
    other.m_payload = nullptr;
    other.m_ptr     = nullptr;
    return *this;
}

template < typename T >
ref< T >::~ref()
{
    if(m_payload && --m_payload->reference_count == 0)
    {
        allocator& a = m_payload->allocator;
        m_payload->~ref_payload();
        a.free(m_payload);
    }
}

template < typename T >
T* ref< T >::operator->() const
{
    return m_ptr;
}

template < typename T >
ref< T >::operator const void*() const
{
    return static_cast< const void* >(m_ptr);
}

template < typename T >
bool ref< T >::operator!() const
{
    return m_ptr == nullptr;
}

template < typename T >
T& ref< T >::operator*()
{
    return *m_ptr;
}

template < typename T >
void ref< T >::clear()
{
    if(m_payload && --m_payload->reference_count == 0)
    {
        allocator& a = m_payload->allocator;
        m_payload->~ref_payload();
        a.free(m_payload);
    }
    m_payload = nullptr;
    m_ptr     = nullptr;
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

template < typename U, typename T >
inline ref< U > motor_checked_cast(const ref< T >& value)
{
    motor_assert(!value || dynamic_cast< U* >(value.m_ptr), "invalid cast");
    return ref< U >(value.m_payload, static_cast< U* >(value.m_ptr));
}

}  // namespace minitl

#endif
