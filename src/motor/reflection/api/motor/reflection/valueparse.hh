/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_PARSE_VALUEPARSE_HH_
#define MOTOR_META_PARSE_VALUEPARSE_HH_
/**************************************************************************************************/
#include <motor/reflection/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>

namespace Motor { namespace Meta {

motor_api(REFLECTION) ref< AST::Node > parseValue(minitl::Allocator& arena,
                                                  AST::MessageList& context, const char* strBegin,
                                                  const char* strEnd = 0, u32 initialLine = 0,
                                                  u32 initialColumn = 0);

motor_api(REFLECTION) Meta::Value
    quickParse(minitl::Allocator& arena, const char* strBegin, const char* strEnd = 0);
}}  // namespace Motor::Meta

/**************************************************************************************************/
#endif
