/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_OBJECT_META_HH
#define MOTOR_META_OBJECT_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

class Class;

class motor_api(META) Object
{
public:
    raw< Object > const      next;
    raw< const Class > const owner;
    istring const            name;
    Value                    value;
};

}}  // namespace Motor::Meta

#include <motor/meta/object.meta.factory.hh>
#endif
