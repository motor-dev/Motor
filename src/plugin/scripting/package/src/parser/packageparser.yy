/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
%{
#include    <motor/plugin.scripting.package/stdafx.h>
#include    <buildcontext.hh>

#include    <motor/reflection/valueparse.hh>

#define yyparse motor_package_parse
#define yylex   motor_package_lex
#define yyerror motor_package_error
#define yylval  motor_package_lval
#define yychar  motor_package_char
#define yydebug motor_package_debug
#define yynerrs motor_package_nerrs



#ifdef _MSC_VER
# include <malloc.h>
# pragma warning(push)
# pragma warning(disable:4065) // switch contains 'default' but no 'case' label
# pragma warning(disable:4244) // conversion from 'type1' to 'type2' : possible loss of data
# pragma warning(disable:4100) // param : unreferenced formal parameter
# pragma warning(disable:4702) // unreachable code
#endif

#define YYSTACK_USE_ALLOCA 1

extern int yylex();

static int yyerror(void* context, const char *msg)
{
    using namespace Motor::Meta::AST;
    Motor::PackageBuilder::BuildContext* buildContext = static_cast<Motor::PackageBuilder::BuildContext*>(context);
    buildContext->result->context().error(weak<const Node>(),
                                          Message::MessageType("%s at line %d (%d:%d)") | msg | (g_packageLine+1)
                                                                                        | (g_packageColumnBefore)
                                                                                        | (g_packageColumnAfter));
    return 0;
}

#ifndef __attribute__
# define __attribute__(x)
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
#define realloc(x,s) Motor::Arena::temporary().realloc(x, s, 4)
#define free(x)      Motor::Arena::temporary().free(x)

using namespace Motor::PackageBuilder;
using namespace Motor::Meta;

%}

%token  TOK_ID TOK_value
%token  KW_import KW_plugin KW_as

%start  file
%parse-param { void*  param }

%type <id> TOK_ID fullname
%type <offset> TOK_value
%destructor { free($$); }                   TOK_ID fullname

%%

file:
        imports
        decls
    ;

imports:
        imports import
    |
        /* empty */
    ;

import:
        decl_import
    |
        decl_plugin
    ;

decls:
        decls decl
    |
        /* empty */
    ;

decl:
        decl_object
    ;

decl_import:
        KW_import fullname ';'
        {
            free($2);
        }
    ;

decl_plugin:
        KW_plugin fullname ';'
            {
                ((BuildContext*)param)->result->loadPlugin($2, $2);
                free($2);
            }
    |
        KW_plugin fullname KW_as TOK_ID ';'
            {
                ((BuildContext*)param)->result->loadPlugin($2, $4);
                free($2);
                free($4);
            }
    ;

decl_object:
        editor_attributes
        TOK_ID '=' TOK_value
        {
            //(*$4)->setName($2);
            BuildContext* context = ((BuildContext*)param);
            ref<AST::Node> node = parseValue(Motor::Arena::package(), context->result->context().messages,
                                             (const char*)g_buffer->data()+$4.start, (const char*)g_buffer->data()+$4.end,
                                             $4.line, $4.column);
            if (node)
            {
                context->result->insertNode($2, node);
            }
            free($2);
        }
    ;

editor_attributes:
        editor_attributes
        '[' attribute ']'
    |
        /* empty */
    ;

attribute:
        TOK_ID '=' TOK_value
        {
            BuildContext* context = ((BuildContext*)param);
            ref<AST::Node> node = parseValue(Motor::Arena::package(), context->result->context().messages,
                                             (const char*)g_buffer->data()+$3.start, (const char*)g_buffer->data()+$3.end,
                                             $3.line, $3.column);
            motor_forceuse(node);
            free($1);
        }
    ;

fullname:
        TOK_ID
        {
            $$ = $1;
        }
    |
        TOK_ID '.' fullname
        {
            size_t s = strlen($1);
            s += strlen($3);
            s++;
            char* result = (char*)malloc(s+1);
            strcpy(result, $1);
            strcat(result, ".");
            strcat(result, $3);
            free($1);
            free($3);
            $$ = result;
        }
    ;
%%
