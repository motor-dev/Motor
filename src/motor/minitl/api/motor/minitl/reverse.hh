/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_REVERSE_HH
#define MOTOR_MINITL_REVERSE_HH

#include <motor/minitl/stdafx.h>

namespace minitl {

namespace reverse_details {

template < typename T >
struct reverse_view;

template < typename T >
struct const_reverse_view;

}  // namespace reverse_details

template < typename CONTAINER >
MOTOR_ALWAYS_INLINE reverse_details::reverse_view< CONTAINER > reverse_view(CONTAINER& container);

template < typename CONTAINER >
MOTOR_ALWAYS_INLINE reverse_details::const_reverse_view< CONTAINER >
                    reverse_view(const CONTAINER& container);

}  // namespace minitl

#include <motor/minitl/inl/reverse.hh>

#endif
