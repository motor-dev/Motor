/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/typeinfo.meta.hh>

namespace Motor { namespace Meta {

struct Tag;
class Value;

struct motor_api(META) Property
{
    friend class Value;
    typedef Value (*Getter)(raw< const Property > property, void* data);
    typedef void (*Setter)(raw< const Property > property, void* data, const Value& value);
published:
    raw< const staticarray< const Tag > > const tags;
    istring const                               name;
    Type const                                  owner;
    Type const                                  type;

    Value get(const Value& from) const;
    void  set(Value & from, const Value& value) const;

    Value getTag(const Type& tagType) const;
    Value getTag(raw< const Class > tagType) const;

public:
    const Getter getter;
    const Setter setter;
};

}}  // namespace Motor::Meta
