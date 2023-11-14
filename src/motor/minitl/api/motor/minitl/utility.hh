/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MINITL_UTILITY_HH
#define MOTOR_MINITL_UTILITY_HH

#include <motor/minitl/stdafx.h>

#include <utility>

namespace minitl {

using std::forward;
using std::move;

template < u32... INDICES >
struct index_sequence
{
};

}  // namespace minitl

#include <motor/minitl/inl/utility.hh>

#endif
