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
from motor_typing import TYPE_CHECKING


@glrp.rule('function-definition : attribute-specifier-seq? declarator function-body')
@glrp.rule('function-definition : attribute-specifier-seq? decl-specifier-seq declarator function-body')
@glrp.rule('function-definition : attribute-specifier-seq? declarator virt-specifier-seq function-body')
@glrp.rule(
    'function-definition : attribute-specifier-seq? decl-specifier-seq declarator virt-specifier-seq function-body'
)
@cxx98
def function_definition(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('function-definition : attribute-specifier-seq? declarator requires-clause function-body')
@glrp.rule('function-definition : attribute-specifier-seq? decl-specifier-seq declarator requires-clause function-body')
@cxx20
def function_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('function-body : compound-statement')
@glrp.rule('function-body : ctor-initializer compound-statement')
@glrp.rule('function-body : function-try-block')
@cxx98
def function_body(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('function-body : "=" "default" ";"')
@glrp.rule('function-body : "=" "delete" ";"')
@cxx11
def function_body_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('function-definition')
@cxx98_merge
def ambiguous_function_definition(self, ambiguous_type_specifier, ambiguous_declarator):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # attribute-specifier-seq? decl-specifier-seq declarator function-body | attribute-specifier-seq? declarator function-body
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ...parser import CxxParser