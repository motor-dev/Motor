/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_INL_TRAITS_HH
#define MOTOR_MINITL_INL_TRAITS_HH
#pragma once

#include <motor/minitl/traits.hh>
#include <string.h>

template <>
struct minitl::less< const char* >
{
    bool operator()(const char* str1, const char* str2) const
    {
        return ::strcmp(str1, str2) < 0;
    }
};  // namespace minitl

#endif
