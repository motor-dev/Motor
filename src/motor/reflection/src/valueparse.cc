/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/reflection/stdafx.h>
#include <motor/meta/value.hh>
#include <motor/reflection/valueparse.hh>
#include <parsecontext.hh>

namespace Motor { namespace Meta {

ref< AST::Node > parseValue(minitl::allocator& arena, AST::MessageList& errors,
                            const char* strBegin, const char* strEnd, u32 initialLine,
                            u32 initialColumn)
{
    Parse::ParseContext context(arena, strBegin, strEnd ? strEnd : (strBegin + strlen(strBegin)),
                                errors, initialLine, initialColumn);
    int                 result = motor_value_parse(&context);
    motor_value_lex_destroy();
    if(result != 0 || !errors.empty())
    {
        return {};
    }
    else
    {
        return context.result;
    }
}

}}  // namespace Motor::Meta
