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
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator begin-function-body function-body'
)
@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator begin-function-body virt-specifier-seq function-body'
)
@cxx98
def function_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    declarator = p[3]
    if not declarator.is_method():
        raise SyntaxError
    pass


@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning]decl-specifier-seq? declarator begin-function-body requires-clause function-body'
)
@cxx20
def function_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-function-body : [split:function_body]')
@cxx98
def begin_function_body(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    declarator = p[-1]
    if not declarator.is_method():
        raise SyntaxError


@glrp.rule('begin-initializer : [split:initializer]')
@cxx98
def begin_function_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    declarator = p[-1]
    if declarator.is_method():
        raise SyntaxError


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


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser