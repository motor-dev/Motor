/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_HELPER_SET_HH_
#define MOTOR_META_ENGINE_HELPER_SET_HH_
/**************************************************************************************************/
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

template < typename T, typename Owner, T(Owner::*Field) >
static inline void set(weak< const Property > /*_this*/, void* from, Value& value, bool isConst)
{
    motor_assert_recover(!isConst, "Setting property on const object", return );
    motor_forceuse(isConst);
    (Owner*)from->*Field = value.as< T >();
}

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
