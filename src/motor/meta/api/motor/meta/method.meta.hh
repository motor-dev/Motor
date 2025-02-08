/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_METHOD_META_HH
#define MOTOR_META_METHOD_META_HH

#include <motor/meta/stdafx.h>

#include <motor/meta/type.meta.hh>
#include <motor/minitl/view.hh>

namespace Motor { namespace Meta {

class Value;
class Tag;

class motor_api(META) Method
{
public:
    class motor_api(META) Parameter
    {
    public:
        raw< const Tag > const   tags;
        istring const            name;
        Type const               type;
        raw< const Value > const defaultValue;

    public:
        Value getTag(const Type& type) const;
        Value getTag(raw< const Class > type) const;

        static const Value s_noDefaultValue;

    public:
        [[motor::meta(export = no)]] static constexpr raw< const Value > noDefaultValue {
            &s_noDefaultValue};
    };
    class motor_api(META) Overload
    {
    public:
        raw< Tag > const                tags;
        minitl::view< Parameter > const parameters;
        Type const                      returnType;
        bool const                      variadic;
        bool const                      member;

    public:
        Value getTag(const Type& tagType) const;
        Value getTag(raw< const Class > tagType) const;

    public:
        [[motor::meta(export = no)]] Value (*call)(raw< const Method > method, Value* params,
                                                   u32 paramCount);
    };

public:
    raw< const Method >      next;
    istring                  name;
    minitl::view< Overload > overloads;

public:
    Value doCall(Value* params, u32 paramCount) const;
};

}}  // namespace Motor::Meta

#include <motor/meta/method.meta.factory.hh>
#endif
