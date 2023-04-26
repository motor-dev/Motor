/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/minitl/stdafx.h>

namespace minitl {

template < typename T >
MOTOR_ALWAYS_INLINE void swap(T& a, T& b)
{
    T c = a;
    a   = b;
    b   = c;
}

}  // namespace minitl
