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
    template < typename T >
    struct ConversionOperators
    {
        Type valueType;
        Value (*construct)(T t);
        T (*get)(const Value& value);
    };
    struct ArrayOperators
    {
        Type valueType;
        Value (*get)(const Value& value, u32 index);
        Value (*getConst)(const Value& value, u32 index);
        u32 (*size)(const Value& value);
    };
    struct MapOperators
    {
        Type keyType;
        Type valueType;
        Value (*get)(const Value& key);
    };
    struct VariantOperators
    {
    };

    raw< const ConversionOperators< bool > >        boolOperators;
    raw< const ConversionOperators< i64 > >         signedIntegerOperators;
    raw< const ConversionOperators< u64 > >         unsignedIntegerOperators;
    raw< const ConversionOperators< float > >       floatOperators;
    raw< const ConversionOperators< double > >      doubleOperators;
    raw< const ConversionOperators< const char* > > stringOperators;
    raw< const VariantOperators >                   variantOperators;
    raw< const ArrayOperators >                     arrayOperators;
    raw< const MapOperators >                       mapOperators;
    raw< const Class >                              resourceType;
    raw< const Method >                             call;
    raw< const Method > (*dynamicCall)(const Value& value);
};

}}  // namespace Motor::Meta

#endif
