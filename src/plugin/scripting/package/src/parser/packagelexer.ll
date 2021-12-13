/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
%{
#include    <motor/plugin.scripting.package/stdafx.h>
#include    <ctype.h>
#include    <buildcontext.hh>
#include    <motor/reflection/valueparse.hh>

#define yylval  motor_package_lval
#include "packageparser.hh"

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

static void update (int num)
{
    g_packageOffset += num;
    g_packageColumnBefore = g_packageColumnAfter;
    g_packageColumnAfter += num;
}
static void newline()
{
    g_packageOffset ++;
    g_packageLine++;
    g_packageColumnBefore = 0;
    g_packageColumnAfter = 1;
}

extern "C" int motor_package_wrap()
{
    return 1;
}

#define YY_INPUT(buf,result,max_size)                               \
        {                                                           \
            result = max_size > g_buffer->count()-g_bufferPosition  \
                ? g_buffer->count()-g_bufferPosition                \
                : max_size;                                         \
            memcpy(buf, g_buffer->data()+g_bufferPosition, result); \
            g_bufferPosition += result;                             \
        }



%}

%option prefix="motor_package_"
%option never-interactive
%option nounput

%x RTTIPARSE

%%

<INITIAL>{
    import {
         update(motor_package_leng);
         return KW_import;
    }

    load {
        update(motor_package_leng);
        return KW_plugin;
    }

    as {
        update(motor_package_leng);
        return KW_as;
    }

    [A-Za-z_][0-9A-Za-z_<>]* {
        update(motor_package_leng);
        yylval.id = motor_strdup(motor_package_text);
        return TOK_ID;
    }

    "\n" {
        (void)&yyinput;
        newline();
    }

    [ \r\t]+ {
        update(motor_package_leng);
    }

    \#[^\n]*\n {
        update(motor_package_leng);
    }

    "=" {
        update(motor_package_leng);
        
        BEGIN(RTTIPARSE);
        yylval.offset.line = g_packageLine;
        yylval.offset.column = g_packageColumnAfter;
        yylval.offset.start = g_packageOffset;
        return *motor_package_text;
    }

    . {
        update(motor_package_leng);
        return *motor_package_text;
    }
}

<RTTIPARSE>{
    ";" {
        update(motor_package_leng);
        if (g_packageObjectNestedLevel == 0)
        {
            BEGIN(INITIAL);
            yylval.offset.end = g_packageOffset-1;
            return TOK_value;
        }
    }

    "(" {
        update(motor_package_leng);
        ++g_packageObjectNestedLevel;
    }

    ")" {
        update(motor_package_leng);
        --g_packageObjectNestedLevel;
    }

    "\n" {
        (void)&yyinput;
        newline();
    }

    . {
        update(motor_package_leng);
    }
}


%%

#ifdef _MSC_VER
#pragma warning(pop)
#endif

#if (YY_FLEX_MINOR_VERSION < 5) || (YY_FLEX_MINOR_VERSION == 5 && YY_FLEX_SUBMINOR_VERSION < 5)
int motor_package_lex_destroy()
{
    yy_delete_buffer(yy_current_buffer);
    yy_init = 1;
    return 0;
}
#endif
