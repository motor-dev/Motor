/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_OBJECTINFO_META_HH_
#define MOTOR_META_ENGINE_OBJECTINFO_META_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

struct Tag;

struct motor_api(META) ObjectInfo
{
    raw< const ObjectInfo > const         next;
    raw< const staticarray< const Tag > > tags;
    istring const                         name;
    mutable Value                         value;
};

}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
