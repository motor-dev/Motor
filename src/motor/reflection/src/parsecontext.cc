/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/introspect/stdafx.h>
#include <parsecontext.hh>

namespace Motor { namespace Meta { namespace Parse {

ParseContext* g_parseContext;
static i_u32  s_useCount;

ParseContext::ParseContext(minitl::Allocator& allocator, const char* bufferStart,
                           const char* bufferEnd, AST::MessageList& errors, u32 lineStart,
                           u32 columnStart)
    : arena(&allocator)
    , result()
    , bufferStart(bufferStart)
    , bufferEnd(bufferEnd)
    , buffer(bufferStart)
    , errors(errors)
    , location()
{
    if(s_useCount++ != 0)
    {
        motor_error(Log::meta(), "RTTI Parser is not reentrant");
    }
    location.line        = lineStart;
    location.columnStart = columnStart;
    location.columnEnd   = columnStart;
    g_parseContext       = this;
}

ParseContext::~ParseContext()
{
    s_useCount--;
    g_parseContext = 0;
}

}}}  // namespace Motor::Meta::Parse
