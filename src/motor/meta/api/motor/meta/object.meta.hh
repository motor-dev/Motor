/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_OBJECT_META_HH
#define MOTOR_META_OBJECT_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

class Tag;

class motor_api(META) Object
{
public:
    raw< const Object > const next;
    istring const             name;
    mutable Value             value;
};

}}  // namespace Motor::Meta

#endif
