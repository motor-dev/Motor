/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_MINITL_VIEW_HH
#define MOTOR_MINITL_VIEW_HH

#include <motor/minitl/stdafx.h>
#include <motor/minitl/span.hh>

namespace minitl {

template < typename T >
class view : public span< const T >
{
public:
    using span< const T >::span;
};

}  // namespace minitl

#endif
