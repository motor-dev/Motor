/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TYPEINFO_INL_
#define MOTOR_META_TYPEINFO_INL_
/**************************************************************************************************/
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

/**************************************************************************************************/
#endif
