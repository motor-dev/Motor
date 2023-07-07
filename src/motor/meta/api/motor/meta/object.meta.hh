/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_OBJECT_META_HH
#define MOTOR_META_OBJECT_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

struct Tag;

struct motor_api(META) Object
{
    raw< const Object > const next;
    raw< const Tag > const    tags;
    istring const             name;
    mutable Value             value;
};

}}  // namespace Motor::Meta

#endif
