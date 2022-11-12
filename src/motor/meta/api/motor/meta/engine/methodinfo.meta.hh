/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/typeinfo.hh>

namespace Motor { namespace Meta {

class Value;
struct Tag;

struct motor_api(META) Method
{
published:
    struct motor_api(META) Parameter
    {
    published:
        raw< const staticarray< const Tag > > tags;
        istring                               name;
        Type                                  type;
        raw< const Value >                    defaultValue;
    published:
        Value getTag(const Type& type) const;
        Value getTag(raw< const Class > type) const;

    public:
        static const Value s_noDefaultValue;
    };
    struct motor_api(META) Overload
    {
    published:
        raw< const staticarray< const Tag > > tags;
        staticarray< const Parameter >        params;
        Type                                  returnType;
        bool                                  vararg;
    published:
        Value getTag(const Type& tagType) const;
        Value getTag(raw< const Class > tagType) const;

    public:
        minitl::format< 1024u > signature() const;
        Value (*call)(raw< const Method > method, Value * params, u32 nparams);
    };

published:
    istring                                       name;
    staticarray< const Overload >                 overloads;
    motor_tag(Alias("?call")) raw< const Method > call;

published:
    Value doCall(Value * params, u32 nparams) const;
};

}}  // namespace Motor::Meta
