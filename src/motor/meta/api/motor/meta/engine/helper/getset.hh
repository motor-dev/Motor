/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

class Value;
struct Property;

template < typename T, typename Owner, T(Owner::*Member) >
struct PropertyHelper
{
    static Value get(raw< const Property > property, void* from)
    {
        motor_forceuse(property);
        const auto* owner = reinterpret_cast< const Owner* >(from);
        return Value::ByRef(owner->*Member);
    }
    static void set(raw< const Property > property, void* from, const Value& value)
    {
        motor_forceuse(property);
        auto* owner = reinterpret_cast< Owner* >(from);
        new(&(owner->*Member)) T(value.as< const T& >());
    }
};

template < typename T, typename Owner, const T(Owner::*Member) >
struct PropertyHelper< const T, Owner, Member >
{
    static Value get(raw< const Property > property, void* from)
    {
        motor_forceuse(property);
        const auto* owner = reinterpret_cast< const Owner* >(from);
        return Value::ByRef(owner->*Member);
    }
    static void set(raw< const Property > property, void* from, const Value& value)
    {
        motor_forceuse(property);
        motor_forceuse(from);
        motor_forceuse(value);
        motor_notreached();
    }
};

}}  // namespace Motor::Meta
