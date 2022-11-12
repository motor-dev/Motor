/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/conversion.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
bool Type::isA() const
{
    return isA(motor_type< T >());
}

}}  // namespace Motor::Meta
