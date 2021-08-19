/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_MINITL_TRAITS_HH_
#define MOTOR_MINITL_TRAITS_HH_
/**************************************************************************************************/
#include <motor/minitl/stdafx.h>
#include <string.h>

namespace minitl {

template < typename T >
struct less;

template <>
struct less< const char* >
{
    bool operator()(const char* str1, const char* str2) const
    {
        return ::strcmp(str1, str2) < 0;
    }
};

}  // namespace minitl

/**************************************************************************************************/
#endif
