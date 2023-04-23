/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

namespace minitl {

template < typename T >
void swap(T& a, T& b)
{
    T c = a;
    a   = b;
    b   = c;
}

}  // namespace minitl
