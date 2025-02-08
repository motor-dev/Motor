/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_PROPERTY_META_HH
#define MOTOR_META_PROPERTY_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/type.meta.hh>

namespace Motor { namespace Meta {

class Tag;
class Value;

class motor_api(META) Property
{
    friend class Value;
    typedef Value (*Getter)(raw< const Property > property, const void* data);
    typedef void (*Setter)(raw< const Property > property, void* data, const Value& value);

public:
    raw< const Property > next;
    raw< const Tag >      tags;
    istring const         name;
    Type const            owner;
    Type const            type;

    Value get(const Value& from) const;
    void  set(Value& from, const Value& value) const;

    Value getTag(const Type& tagType) const;
    Value getTag(raw< const Class > tagType) const;

public:
    [[motor::meta(export = no)]] const Getter getter;
    [[motor::meta(export = no)]] const Setter setter;
};

}}  // namespace Motor::Meta

#include <motor/meta/property.meta.factory.hh>
#endif
