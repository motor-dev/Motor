/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
%{
#include    <motor/introspect/stdafx.h>
#include    <ctype.h>
#include    <parsecontext.hh>

#define yylval  motor_value_lval
#include "valueparser.hh"

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable:4127 4244 4267 4996 4505)
#endif

#ifdef malloc
# undef malloc
#endif
#ifdef realloc
# undef realloc
#endif
#ifdef free
# undef free
#endif
#define malloc(x)    Motor::Arena::temporary().alloc(x, 4)
#define relloc(x,s)  Motor::Arena::temporary().realloc(x, s, 4)
#define free(x)      Motor::Arena::temporary().free(x)
#ifdef strdup
# undef strdup
#endif
#define strdup(x)    motor_strdup(x)

static char *motor_strdup(const char *src)
{
    size_t x = strlen(src);
    char* result = (char*)malloc(x+1);
    strncpy(result, src, x+1);
    return result;
}

static i64 strToInteger(const char *text, size_t l)
{
    bool negate = false;
    i64 result = 0;
    if (*text == '-')
    {
        negate = true;
        text++;
        l--;
    }
    for (size_t i = 0; i < l; ++i)
    {
        result = result * 10 + (text[i]-'0');
    }
    return negate?-result:result;
}

static double strToDouble(const char *text, size_t /*l*/)
{
    return strtod(text, 0);
}

static void update (int num)
{
    ::Motor::Meta::Parse::g_parseContext->location.update(num);
}

static void newline()
{
    ::Motor::Meta::Parse::g_parseContext->location.newline();
}

extern "C" int motor_value_wrap()
{
    return 1;
}

#define YY_INPUT(buf,result,max_size)                                               \
        {                                                                           \
            using namespace ::Motor::Meta::Parse;                               \
            result = max_size > g_parseContext->bufferEnd - g_parseContext->buffer  \
                ? g_parseContext->bufferEnd - g_parseContext->buffer                \
                : max_size;                                                         \
            memcpy(buf, g_parseContext->buffer, result);                            \
            g_parseContext->buffer += result;                                       \
        }



%}

%option prefix="motor_value_"
%option never-interactive
%option nounput

DIGIT           [0-9]
HEXDIGIT        [0-9A-Fa-f]
DIGITS          ({DIGIT}+)
SIGN            ("+"|"-")
ID              [A-Za-z_][0-9A-Za-z_<>]*

%%

true                                            { update(motor_value_leng);
                                                  yylval.bValue.value = true;
                                                  yylval.bValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return VAL_BOOLEAN; }
false                                           { update(motor_value_leng);
                                                  yylval.bValue.value = false;
                                                  yylval.bValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return VAL_BOOLEAN; }
{ID}                                            { update(motor_value_leng);
                                                  yylval.sValue.value = motor_strdup(motor_value_text);
                                                  yylval.sValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return TOK_ID; }
\"[^\r\n\"]*\"                                  { update(motor_value_leng);
                                                  yylval.sValue.value = motor_strdup(motor_value_text+1);
                                                  yylval.sValue.value[motor_value_leng-2] = 0;
                                                  yylval.sValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return VAL_STRING; }
@\"[^\r\n\"]*\"                                 { update(motor_value_leng);
                                                  yylval.sValue.value = motor_strdup(motor_value_text+2);
                                                  yylval.sValue.value[motor_value_leng-3] = 0;
                                                  yylval.sValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return VAL_FILENAME; }
-?[0-9]+                                        { update(motor_value_leng);
                                                  yylval.iValue.value = strToInteger(motor_value_text, motor_value_leng);
                                                  yylval.iValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return VAL_INTEGER; }
{DIGITS}("."{DIGITS}?)?([eE]{SIGN}?{DIGITS})?   { update(motor_value_leng);
                                                  yylval.fValue.value = strToDouble(motor_value_text, motor_value_leng);
                                                  yylval.fValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return VAL_FLOAT; }
"\n"                                            { (void)&yyinput; newline(); }
[ \r\t]+                                        { update(motor_value_leng); }
\#[^\n]*\n                                      { update(motor_value_leng); }
.                                               { update(motor_value_leng);
                                                  yylval.cValue.value = *motor_value_text;
                                                  yylval.cValue.location = ::Motor::Meta::Parse::g_parseContext->location;
                                                  return *motor_value_text; }

%%

#ifdef _MSC_VER
#pragma warning(pop)
#endif

#if (YY_FLEX_MINOR_VERSION < 5) || (YY_FLEX_MINOR_VERSION == 5 && YY_FLEX_SUBMINOR_VERSION < 5)
int motor_value_lex_destroy()
{
    yy_delete_buffer(yy_current_buffer);
    return 0;
}
#endif
