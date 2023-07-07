/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_INL_TYPEINFO_HH
#define MOTOR_META_INL_TYPEINFO_HH
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

template < typename T >
bool Type::isA() const
{
    return isA(motor_type< T >());
}

}}  // namespace Motor::Meta

#endif
