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
from ...parser import cxx98, cxx11, cxx20, cxx98_merge
from ....ast.declarations import AmbiguousDeclaration
from motor_typing import TYPE_CHECKING


@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-function-body function-body'
)
@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-function-body virt-specifier-seq function-body'
)
@cxx98
def function_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator-function-body requires-clause function-body'
)
@cxx20
def function_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('declarator-function-body : declarator [split:function_body]')
@cxx98
def begin_function_body(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    declarator = p[0]
    if not declarator.is_method():
        raise SyntaxError
    return declarator


@glrp.rule('declarator-initializer : declarator [split:initializer]')
@cxx98
def begin_function_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    declarator = p[0]
    if declarator.is_method():
        raise SyntaxError
    return declarator


@glrp.rule('function-body : compound-statement')
@glrp.rule('function-body : ctor-initializer compound-statement')
@glrp.rule('function-body : function-try-block')
@cxx98
def function_body(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('function-body : "=" "default" ";"')
@glrp.rule('function-body : "=" "delete" ";"')
@cxx11
def function_body_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('function-definition')
@cxx98_merge
def ambiguous_function_definition(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousDeclaration(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('function-definition')
@cxx98_merge
def ambiguous_function_definition_final(self, final_keyword, final_identifier):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser