/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_MINITL_INTEGER_TYPES_HH
#define MOTOR_MINITL_INTEGER_TYPES_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

template < u32 BYTE_COUNT >
struct integer_type;

template < u32 BYTE_COUNT >
using signed_integer_type_t = typename integer_type< BYTE_COUNT >::signed_type;
template < u32 BYTE_COUNT >
using unsigned_integer_type_t = typename integer_type< BYTE_COUNT >::unsigned_type;

}  // namespace minitl

#include <motor/minitl/inl/integer_types.hh>

#endif
