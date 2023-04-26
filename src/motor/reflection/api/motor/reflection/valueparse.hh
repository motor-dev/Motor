/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/reflection/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

motor_api(REFLECTION) ref< AST::Node > parseValue(minitl::allocator& arena,
                                                  AST::MessageList& context, const char* strBegin,
                                                  const char* strEnd = nullptr, u32 initialLine = 0,
                                                  u32 initialColumn = 0);

motor_api(REFLECTION) Meta::Value
    quickParse(minitl::allocator& arena, const char* strBegin, const char* strEnd = nullptr);
}}  // namespace Motor::Meta
