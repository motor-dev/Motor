/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_METHOD_META_HH
#define MOTOR_META_METHOD_META_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/typeinfo.hh>

#include <motor/minitl/view.hh>

namespace Motor { namespace Meta {

class Value;
struct Tag;

struct motor_api(META) Method
{
published:
    struct motor_api(META) Parameter
    {
    published:
        raw< const Tag > const   tags;
        istring const            name;
        Type const               type;
        raw< const Value > const defaultValue;
    published:
        Value getTag(const Type& type) const;
        Value getTag(raw< const Class > type) const;

        static const Value s_noDefaultValue;

    public:
        static constexpr raw< const Value > noDefaultValue {&s_noDefaultValue};
    };
    struct motor_api(META) Overload
    {
    published:
        raw< Tag > const                tags;
        minitl::view< Parameter > const parameters;
        Type const                      returnType;
        bool const                      variadic;
    published:
        Value getTag(const Type& tagType) const;
        Value getTag(raw< const Class > tagType) const;

    public:
        Value (*call)(raw< const Method > method, Value* params, u32 paramCount);
    };

published:
    raw< const Method >      next;
    istring                  name;
    minitl::view< Overload > overloads;

published:
    Value doCall(Value * params, u32 nparams) const;
};

}}  // namespace Motor::Meta

#endif
