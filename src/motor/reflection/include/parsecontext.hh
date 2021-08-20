/* Motor <motor.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef MOTOR_META_PARSE_PARSECONTEXT_HH_
#define MOTOR_META_PARSE_PARSECONTEXT_HH_
/**************************************************************************************************/
#include <motor/reflection/stdafx.h>
#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/node.hh>
#include <motor/introspect/node/object.hh>
#include <motor/reflection/location.meta.hh>

template < typename T >
struct ParseResult
{
    Motor::Meta::Parse::Location location;
    T                            value;
};

union YYSTYPE
{
    ParseResult< bool >                                                  bValue;
    ParseResult< i64 >                                                   iValue;
    ParseResult< double >                                                fValue;
    ParseResult< char >                                                  cValue;
    ParseResult< char* >                                                 sValue;
    ParseResult< ref< Motor::Meta::AST::Node >* >                        value;
    ParseResult< ref< Motor::Meta::AST::Parameter >* >                   param;
    ParseResult< minitl::vector< ref< Motor::Meta::AST::Parameter > >* > param_list;
    ParseResult< minitl::vector< ref< Motor::Meta::AST::Node > >* >      value_list;
};
#define YYSTYPE_IS_DECLARED 1
#define YYSTYPE_IS_TRIVIAL  1

namespace Motor { namespace Meta { namespace Parse {

struct ParseContext
{
    minitl::Allocator* arena;
    ref< AST::Node >   result;
    const char*        bufferStart;
    const char*        bufferEnd;
    const char*        buffer;
    AST::MessageList&  errors;
    Location           location;

    ParseContext(minitl::Allocator& arena, const char* bufferStart, const char* bufferEnd,
                 AST::MessageList& errors, u32 lineStart = 0, u32 columnStart = 0);
    ~ParseContext();
};

extern ParseContext* g_parseContext;

}}}  // namespace Motor::Meta::Parse

extern "C" int motor_value_parse(Motor::Meta::Parse::ParseContext* context);
extern "C" int motor_value_lex_destroy();

/**************************************************************************************************/
#endif
