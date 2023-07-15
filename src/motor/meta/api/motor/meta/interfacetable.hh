/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_META_INTERFACETABLE_HH
#define MOTOR_META_INTERFACETABLE_HH

#include <motor/meta/stdafx.h>
#include <motor/meta/type.meta.hh>

namespace Motor { namespace Meta {

class Method;
class Value;

class InterfaceTable
{
public:
    template < typename T >
    struct TypeInterface
    {
        Type valueType;
        Value (*construct)(T t);
        T (*get)(const Value& value);
    };
    struct ArrayInterface
    {
        Type valueType;
        Value (*get)(const Value& array, u32 index);
        Value (*getConst)(const Value& array, u32 index);
        void (*set)(const Value& array, u32 index, const Value& value);
        u32 (*size)(const Value& array);
        /* optional */
        Value (*construct)(Value values[], u32 count);
    };
    struct MapInterface
    {
        Type keyType;
        Type valueType;
        Value (*get)(const Value& key);
    };

    raw< const TypeInterface< bool > >        boolInterface;
    raw< const TypeInterface< i64 > >         i64Interface;
    raw< const TypeInterface< u64 > >         u64Interface;
    raw< const TypeInterface< float > >       floatInterface;
    raw< const TypeInterface< double > >      doubleInterface;
    raw< const TypeInterface< const char* > > charpInterface;
    raw< const TypeInterface< Value > >       variantInterface;
    raw< const ArrayInterface >               arrayInterface;
    raw< const MapInterface >                 mapInterface;
    raw< const Class >                        resourceType;
    raw< const Method >                       call;
    raw< const Method > (*dynamicCall)(const Value& value);
};

}}  // namespace Motor::Meta

#endif
