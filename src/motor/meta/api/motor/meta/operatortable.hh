/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_OPERATORTABLE_HH
#define MOTOR_META_OPERATORTABLE_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/type.meta.hh>

namespace Motor { namespace Meta {

struct Method;
class Value;

struct OperatorTable
{
    struct ArrayOperators
    {
        Type valueType;
        Value (*get)(u32 index);
    };
    struct MapOperators
    {
        Type keyType;
        Type valueType;
        Value (*get)(const Value& key);
    };
    struct StringOperators
    {
        Value (*construct)(const char* string);
    };
    struct IntegerOperators
    {
    };
    struct FloatOperators
    {
    };
    struct VariantOperators
    {
    };

    raw< const ArrayOperators >   arrayOperators;
    raw< const MapOperators >     mapOperators;
    raw< const StringOperators >  stringOperators;
    raw< const IntegerOperators > integerOperators;
    raw< const FloatOperators >   floatOperators;
    raw< const VariantOperators > variantOperators;
    raw< const Class >            resourceType;
    raw< const Method >           call;
    raw< const Method > (*dynamicCall)(const Value& value);
};

}}  // namespace Motor::Meta

#endif
