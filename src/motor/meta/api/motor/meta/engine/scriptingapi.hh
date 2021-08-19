/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_SCRIPTINGAPI_HH_
#define MOTOR_META_ENGINE_SCRIPTINGAPI_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

struct ScriptingArrayAPI
{
    Type value_type;
    u32 (*size)(const Value& owner);
    Value (*index)(Value& owner, u32 index);
    Value (*indexConst)(const Value& owner, u32 index);
};

struct ScriptingAPI
{
    raw< const ScriptingArrayAPI > arrayScripting;
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
