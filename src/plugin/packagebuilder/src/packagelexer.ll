%{
#include    <stdafx.h>
#include    <ctype.h>
#include    <buildcontext.hh>

#define yylval  be_package_lval
#include "packageparser.hh"

#pragma warning(disable:4127 4244 4267 4996 4505)

i64 strToInteger(const char *text, size_t l)
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

static void update (int num)
{
    g_packageColumnBefore = g_packageColumnAfter;
    g_packageColumnAfter += num;
}
static void newline()
{
    g_packageLine++;
    g_packageColumnBefore = 0;
    g_packageColumnAfter = 1;
}

extern "C" int be_package_wrap()
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

%option prefix="be_package_"
%option nounput

%%

true                                    { update(be_package_leng); yylval.bValue = true; return VAL_BOOLEAN; }
false                                   { update(be_package_leng); yylval.bValue = false; return VAL_BOOLEAN; }
import                                  { update(be_package_leng); return KW_import; }
plugin                                  { update(be_package_leng); return KW_plugin; }
[0-9A-Za-z_]*[A-Za-z_]+[0-9A-Za-z_]*    { update(be_package_leng); yylval.sValue = strdup(be_package_text); return TOK_ID; }
\"[^\r\n\"]*\"                          { update(be_package_leng); yylval.sValue = strdup(be_package_text+1); yylval.sValue[be_package_leng-2] = 0; return VAL_STRING; }
-?[0-9]+                                { update(be_package_leng); yylval.iValue = strToInteger(be_package_text, be_package_leng); return VAL_INTEGER; }
"\n"                                    { newline(); }
[ \r\t]+                                { update(be_package_leng); }
.                                       { update(be_package_leng); return *be_package_text; }

%%

static struct Cleanup
{
    Cleanup()
    {
    }
    ~Cleanup()
    {
        if (YY_CURRENT_BUFFER)
        {
            yy_delete_buffer(YY_CURRENT_BUFFER);
        }
    }
} cleanup;