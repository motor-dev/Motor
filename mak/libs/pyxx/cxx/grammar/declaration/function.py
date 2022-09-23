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


@glrp.rule('function-definition : attribute-specifier-seq? begin-declaration declarator function-body')
@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning] decl-specifier-seq begin-declarator-no-initializer declarator function-body'
)
@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration declarator virt-specifier-seq function-body'
)
@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning] decl-specifier-seq begin-declarator-no-initializer declarator virt-specifier-seq function-body'
)
@cxx98
def function_definition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('function-definition : attribute-specifier-seq? begin-declaration declarator requires-clause function-body')
@glrp.rule(
    'function-definition : attribute-specifier-seq? begin-declaration [no-merge-warning] decl-specifier-seq  begin-declarator-no-initializer declarator requires-clause function-body'
)
@cxx20
def function_definition_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


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


#@glrp.merge('function-definition')
#@cxx98_merge
#def ambiguous_function_definition(self, ambiguous_function_definition_declspec, decl_declspec, decl_nodeclspec):
#    # type: (CxxParser, List[Any], List[Any]) -> Any
#    pass


@glrp.merge('function-definition')
@cxx98_merge
def ambiguous_function_definition_declspec(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser