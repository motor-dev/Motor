/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/refptr.hh>
#include <motor/minitl/scopedptr.hh>

namespace minitl {

template < typename T >
class weak
{
    template < typename U, typename V >
    friend weak< U > motor_checked_cast(weak< V > v);

private:
    T* m_ptr;

private:
    inline void swap(weak& other);

public:
    inline weak();
    inline weak(T* p);  // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(ref< U > other);  // NOLINT(google-explicit-constructor)
    template < typename U >
    inline weak(const scoped< U >& other);  // NOLINT(google-explicit-constructor)
    inline weak(const weak& other);
    template < typename U >
    inline weak(const weak< U >& other);  // NOLINT(google-explicit-constructor)
    inline ~weak();

    inline weak& operator=(const weak& other);
    template < typename U >
    inline weak& operator=(const weak< U >& other);
    template < typename U >
    inline weak& operator=(U* other);

    MOTOR_ALWAYS_INLINE T* operator->() const;
    inline                 operator const void*() const;  // NOLINT(google-explicit-constructor)
    inline bool            operator!() const;
    MOTOR_ALWAYS_INLINE T& operator*();

    inline void clear();
};

template < typename T >
struct hash< weak< T > >
{
    u32 operator()(weak< T > t)
    {
        return hash< T* >()(t.operator->());
    }
    bool operator()(weak< T > t1, weak< T > t2)
    {
        return hash< T* >()(t1.operator->(), t2.operator->());
    }
};

}  // namespace minitl

#include <motor/minitl/stdafx.h>
#include <motor/minitl/hash.hh>
#include <motor/minitl/refcountable.hh>
#include <motor/minitl/refptr.hh>
#include <motor/minitl/scopedptr.hh>

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
weak< T >::weak(ref< U > other) : m_ptr(check_is_a< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
template < typename U >
weak< T >::weak(const scoped< U >& other) : m_ptr(check_is_a< T >(other.operator->()))
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
weak< T >::weak(const weak< U >& other) : m_ptr(check_is_a< T >(other.operator->()))
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
#endif
}

template < typename T >
weak< T >::~weak()
{
#if MOTOR_ENABLE_WEAKCHECK
    if(m_ptr) m_ptr->add_weak();
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

}  // namespace minitl
