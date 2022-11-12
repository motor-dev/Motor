/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < class T, T v >
struct integral_constant;

typedef integral_constant< bool, true >  true_type;
typedef integral_constant< bool, false > false_type;

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

}  // namespace minitl

#include <motor/minitl/inl/type_traits.inl>
