/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < class T, T V >
struct integral_constant;

typedef integral_constant< bool, true >  true_t;
typedef integral_constant< bool, false > false_t;

template < typename T >
struct is_const;

template < typename T >
struct remove_const;

template < class T >
using remove_const_t = typename remove_const< T >::type;

template < typename T >
struct remove_cv;

template < class T >
using remove_cv_t = typename remove_cv< T >::type;

template < typename T >
struct is_reference;

template < typename T >
struct remove_reference;

template < class T >
using remove_reference_t = typename remove_reference< T >::type;

template < typename T1, typename T2 >
struct is_same;

template < bool CONDITION, typename T = void >
struct enable_if;

template < bool CONDITION, typename T = void >
using enable_if_t = typename enable_if< CONDITION, T >::type;

template < class T >
struct decay;

template < class T >
using decay_t = typename decay< T >::type;

template < class T >
struct unwrap_reference;

template < class T >
struct unwrap_ref_decay;

template < class T >
using unwrap_reference_t = typename unwrap_reference< T >::type;

template < class T >
using unwrap_ref_decay_t = typename unwrap_ref_decay< T >::type;

template < class T >
class reference_wrapper;

template < class T >
reference_wrapper< T > byref(T& t) noexcept;

template < typename T >
struct make_signed;

template < typename T >
using make_signed_t = typename make_signed< T >::type;

template < typename T >
struct make_unsigned;

template < typename T >
using make_unsigned_t = typename make_unsigned< T >::type;

template < class T, T V >
struct integral_constant
{
    static constexpr T value = V;
    using value_t            = T;
    using type               = integral_constant;

    constexpr operator value_t() const noexcept  // NOLINT(google-explicit-constructor)
    {
        return value;
    }
    constexpr value_t operator()() const noexcept
    {
        return value;
    }
};

template < typename T >
struct is_const : public false_t
{
};

template < typename T >
struct is_const< const T > : public true_t
{
};

template < typename T >
struct remove_const
{
    typedef T type;
};
template < typename T >
struct remove_const< const T >
{
    typedef T type;
};

template < typename T >
struct remove_cv
{
    typedef T type;
};

template < typename T >
struct remove_cv< const T >
{
    typedef T type;
};

template < typename T >
struct remove_cv< const volatile T >
{
    typedef T type;
};

template < typename T >
struct remove_cv< volatile T >
{
    typedef T type;
};

template < typename T >
struct is_reference : public false_t
{
};

template < typename T >
struct is_reference< T& > : public true_t
{
};

template < typename T >
struct is_reference< T&& > : public true_t
{
};

template < typename T >
struct remove_reference
{
    typedef T type;
};

template < typename T >
struct remove_reference< T& >
{
    typedef T type;
};

template < typename T >
struct remove_reference< T&& >
{
    typedef T type;
};

template < bool CONDITION, typename T >
struct enable_if
{
};

template < typename T >
struct enable_if< true, T >
{
    typedef T type;
};

template < bool CONDITION, typename T >
using enable_if_t = typename enable_if< CONDITION, T >::type;

template < class T >
struct decay
{
public:
    typedef typename remove_cv< typename remove_reference< T >::type >::type type;
};

template < class T >
struct unwrap_reference
{
    using type = T;
};

template < class U >
struct unwrap_reference< reference_wrapper< U > >
{
    using type = U&;
};

template < class T >
struct unwrap_ref_decay : unwrap_reference< decay_t< T > >
{
};

template < class T >
class reference_wrapper
{
public:
    typedef T wrapped_t;

    constexpr reference_wrapper(T&& t) noexcept : m_ptr(&t)  // NOLINT(google-explicit-constructor)
    {
    }

    reference_wrapper(const reference_wrapper&) noexcept = default;

    reference_wrapper& operator=(const reference_wrapper& x) noexcept = default;

    constexpr operator T&() const noexcept  // NOLINT(google-explicit-constructor)
    {
        return *m_ptr;
    }
    constexpr T& get() const noexcept
    {
        return *m_ptr;
    }

private:
    T* m_ptr;
};

template < class T >
reference_wrapper< T > byref(T& t) noexcept
{
    return reference_wrapper< T >(move(t));
}

template <>
struct make_signed< char >
{
    typedef signed char type;
};

template <>
struct make_signed< signed char >
{
    typedef signed char type;
};

template <>
struct make_signed< signed short >
{
    typedef signed short type;
};

template <>
struct make_signed< signed int >
{
    typedef signed int type;
};

template <>
struct make_signed< signed long int >
{
    typedef signed long int type;
};

template <>
struct make_signed< signed long long int >
{
    typedef signed long long int type;
};

template <>
struct make_signed< unsigned char >
{
    typedef signed char type;
};

template <>
struct make_signed< unsigned short >
{
    typedef signed short type;
};

template <>
struct make_signed< unsigned int >
{
    typedef signed int type;
};

template <>
struct make_signed< unsigned long int >
{
    typedef signed long int type;
};

template <>
struct make_signed< unsigned long long int >
{
    typedef signed long long int type;
};

template <>
struct make_unsigned< char >
{
    typedef unsigned char type;
};

template <>
struct make_unsigned< signed char >
{
    typedef unsigned char type;
};

template <>
struct make_unsigned< signed short >
{
    typedef unsigned short type;
};

template <>
struct make_unsigned< signed int >
{
    typedef unsigned int type;
};

template <>
struct make_unsigned< signed long int >
{
    typedef unsigned long int type;
};

template <>
struct make_unsigned< signed long long int >
{
    typedef unsigned long long int type;
};

template <>
struct make_unsigned< unsigned char >
{
    typedef unsigned char type;
};

template <>
struct make_unsigned< unsigned short >
{
    typedef unsigned short type;
};

template <>
struct make_unsigned< unsigned int >
{
    typedef unsigned int type;
};

template <>
struct make_unsigned< unsigned long int >
{
    typedef unsigned long int type;
};

template <>
struct make_unsigned< unsigned long long int >
{
    typedef unsigned long long int type;
};
}  // namespace minitl
