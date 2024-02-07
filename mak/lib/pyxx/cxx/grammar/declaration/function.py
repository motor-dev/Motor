"""
function-definition:
    attribute-specifier-seq? decl-specifier-seq? declarator virt-specifier-seq? function-body
    attribute-specifier-seq? decl-specifier-seq? declarator requires-clause function-body

function-body:
    ctor-initializer? compound-statement
    function-try-block
    = default ;
    = delete ;
"""

import glrp
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx11, cxx20, cxx98_merge
from ....ast.declarations import AmbiguousDeclaration, ErrorDeclaration
from ....ast.function import FunctionDefinition, DeletedFunctionBody, DefaultFunctionBody, StatementFunctionBody


@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-function-body function-body'
)
@cxx98
def function_definition(self: CxxParser, p: glrp.Production) -> Any:
    return FunctionDefinition(p[0], p[2], p[3], None, [], p[4])


@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-function-body virt-specifier-seq function-body'
)
@cxx98
def function_definition_virt_specifier(self: CxxParser, p: glrp.Production) -> Any:
    return FunctionDefinition(p[0], p[2], p[3], None, p[4], p[5])


@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-function-body requires-clause function-body'
)
@cxx20
def function_definition_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return FunctionDefinition(p[0], p[2], p[3], p[4], [], p[5])


@glrp.rule('function-definition : attribute-specifier-seq? begin-declaration "#error" function-body')
@cxx20
def function_definition_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorDeclaration()


@glrp.rule('declarator-function-body : declarator [split:function_body]')
@cxx98
def begin_function_body(self: CxxParser, p: glrp.Production) -> Any:
    declarator = p[0]
    if not declarator.is_method():
        raise SyntaxError
    return declarator


@glrp.rule('declarator-initializer : declarator [split:initializer]')
@cxx98
def begin_function_initializer(self: CxxParser, p: glrp.Production) -> Any:
    declarator = p[0]
    if declarator.is_method():
        raise SyntaxError
    return declarator


@glrp.rule('function-body : compound-statement')
@cxx98
def function_body(self: CxxParser, p: glrp.Production) -> Any:
    return StatementFunctionBody(None, p[0])


@glrp.rule('function-body : ctor-initializer compound-statement')
@cxx98
def function_body_ctor(self: CxxParser, p: glrp.Production) -> Any:
    return StatementFunctionBody(p[0], p[1])


@glrp.rule('function-body : function-try-block')
@cxx98
def function_body_try_block(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('function-body : "=" "default" ";"')
@cxx11
def function_body_default_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return DefaultFunctionBody()


@glrp.rule('function-body : "=" "delete" ";"')
@cxx11
def function_body_delete_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return DeletedFunctionBody()


@glrp.merge('function-definition')
@cxx98_merge
def ambiguous_function_definition(
        self: CxxParser, decl_specifier_seq_end: List[Any], decl_specifier_seq_continue: List[Any]
) -> Any:
    return AmbiguousDeclaration(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('function-definition')
@cxx98_merge
def ambiguous_function_definition_final(self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)
