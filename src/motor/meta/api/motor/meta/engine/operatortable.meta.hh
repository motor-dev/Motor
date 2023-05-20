/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

struct ArrayOperatorTable
{
public:
    Type value_type {};
    u32 (*size)(const Value& owner) {};
    Value (*index)(Value& owner, u32 index) {};
    Value (*indexConst)(const Value& owner, u32 index) {};
};

struct OperatorTable
{
    raw< const ArrayOperatorTable > arrayOperators {};
    staticarray< const Method >     casts {};
    raw< const Meta::Class >        templatedClass {};

    motor_api(META) static raw< const OperatorTable > s_emptyTable;
};

}}  // namespace Motor::Meta
