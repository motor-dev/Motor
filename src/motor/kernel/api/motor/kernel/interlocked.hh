/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_KERNEL_INTERLOCKED_HH
#define MOTOR_KERNEL_INTERLOCKED_HH

#include <motor/kernel/stdafx.h>

#if defined(MOTOR_COMPILER_MSVC) || (defined(MOTOR_COMPILER_INTEL) && defined(_WIN32))
#    if defined(_X86)
#        include <motor/kernel/msvc/x86/interlocked.inl>
#    elif defined(_AMD64)
#        include <motor/kernel/msvc/amd64/interlocked.inl>
#    elif defined(_PPC)
#        include <motor/kernel/msvc/ppc/interlocked.inl>
#    elif defined(_ARM64)
#        include <motor/kernel/msvc/arm64/interlocked.inl>
#    elif defined(_ARM)
#        include <motor/kernel/msvc/arm/interlocked.inl>
#    else
#        error Architecture not implemented on MSVC
#    endif
#elif defined(MOTOR_COMPILER_SUNCC)
#    include <motor/kernel/suncc/interlocked.inl>
#elif defined(MOTOR_COMPUTE)
#    include <motor/kernel/compute/interlocked.inl>
#elif defined(MOTOR_COMPILER_INTEL) || defined(MOTOR_COMPILER_GCC) || defined(MOTOR_COMPILER_CLANG)
#    if defined(BE_THREAD_SANITIZER)
#        include <motor/kernel/gcc/tsan/interlocked.inl>
#    elif defined(_X86) || defined(_AMD64)
#        include <motor/kernel/gcc/x86/interlocked.inl>
#    elif defined(_POWERPC)
#        include <motor/kernel/gcc/ppc/interlocked.inl>
#    elif defined(_ARM64) && defined(_ILP32)
#        include <motor/kernel/gcc/arm64_32/interlocked.inl>
#    elif defined(_ARM64)
#        include <motor/kernel/gcc/arm64/interlocked.inl>
#    elif defined(_ARM)
#        include <motor/kernel/gcc/arm/interlocked.inl>
#    else
#        error Architecture not implemented on GCC
#    endif
#else
#    error Compiler not implemented
#endif

namespace knl {

template < typename T >
struct interlocked
{
private:
    typedef InterlockedType< sizeof(T) > impl;
    typedef typename impl::value_t       value_t;

private:
    value_t m_value;

public:
    __host __device static interlocked< T > create(T value)
    {
        interlocked< T > result {};
        result.m_value = value_t(value);
        return result;
    }

    __host __device operator T() const  // NOLINT(google-explicit-constructor)
    {
        return static_cast< T >(impl::fetch(&m_value));
    }
    __host __device void set(T value)
    {
        impl::set_and_fetch(&m_value, value);
    }
    __host __device T exchange(T value)
    {
        return static_cast< T >(impl::fetch_and_set(&m_value, value));
    }
    __host __device T addExchange(T value)
    {
        return static_cast< T >(impl::fetch_and_add(&m_value, value));
    }

    __host __device T operator++()
    {
        return static_cast< T >(impl::fetch_and_add(&m_value, 1) + 1);
    }
    __host __device const T operator++(int)  // NOLINT(readability-const-return-type)
    {
        return static_cast< T >(impl::fetch_and_add(&m_value, 1));
    }
    __host __device T operator+=(T value)
    {
        return static_cast< T >(impl::fetch_and_add(&m_value, value) + value);
    }
    __host __device T operator--()
    {
        return static_cast< T >(impl::fetch_and_sub(&m_value, 1) - 1);
    }
    __host __device const T operator--(int)  // NOLINT(readability-const-return-type)
    {
        return static_cast< T >(impl::fetch_and_sub(&m_value, 1));
    }
    __host __device T operator-=(T value)
    {
        return static_cast< T >(impl::fetch_and_sub(&m_value, value) - value);
    }

    __host __device T setConditional(T value, T condition)
    {
        return static_cast< T >(impl::set_conditional(&m_value, value, condition));
    }
};

template < typename T >
struct iptr
{
private:
    typedef InterlockedType< sizeof(T*) > impl;
    typedef typename impl::value_t        value_t;

private:
    value_t m_value;

public:
    __host __device explicit iptr(T* t) : m_value((typename impl::value_t)(t))
    {
    }
    __host __device operator const T*() const  // NOLINT(google-explicit-constructor)
    {
        return static_cast< T >(impl::load(&m_value));
    }
    __host __device operator T*()  // NOLINT(google-explicit-constructor)
    {
        return reinterpret_cast< T* >(impl::fetch_and_add(&m_value, 0));
    }
    __host __device T* operator->()
    {
        return reinterpret_cast< T* >(impl::fetch_and_add(&m_value, 0));
    }
    __host __device const T* operator->() const
    {
        return reinterpret_cast< T* >(impl::fetch_and_add(&m_value, 0));
    }

    __host __device iptr< T >& operator=(T* value)
    {
        impl::set_and_fetch((value_t*)&m_value, (value_t)value);
        return *this;
    }
    __host __device T* exchange(T* value)
    {
        return reinterpret_cast< T* >(impl::fetch_and_set((value_t*)&m_value, (value_t)value));
    }

    __host __device T* setConditional(T* value, T* condition)
    {
        return reinterpret_cast< T* >(
            impl::set_conditional((value_t*)&m_value, (value_t)value, (value_t)condition));
    }
};

}  // namespace knl

typedef knl::interlocked< bool >   i_bool;
typedef knl::interlocked< u8 >     i_u8;
typedef knl::interlocked< u16 >    i_u16;
typedef knl::interlocked< u32 >    i_u32;
typedef knl::interlocked< i8 >     i_i8;
typedef knl::interlocked< i16 >    i_i16;
typedef knl::interlocked< i32 >    i_i32;
typedef knl::interlocked< size_t > i_size_t;
using knl::iptr;

#endif
