"""
statement:
    labeled-statement
    attribute-specifier-seq? expression-statement
    attribute-specifier-seq? compound-statement
    attribute-specifier-seq? selection-statement
    attribute-specifier-seq? iteration-statement
    attribute-specifier-seq? jump-statement
    declaration-statement
    attribute-specifier-seq? try-block

init-statement:
    expression-statement
    simple-declaration

condition:
    expression
    attribute-specifier-seq? decl-specifier-seq declarator brace-or-equal-initializer
"""

import glrp
from ...parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import labeled
from . import expression
from . import block
from . import selection
from . import iteration
from . import jump
from . import declaration


@glrp.rule('statement : labeled-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement expression-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement compound-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement selection-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement iteration-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement jump-statement')
@glrp.rule('statement : declaration-statement')
@glrp.rule('statement : attribute-specifier-seq? begin-expression-statement try-block')
@cxx98
def statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('init-statement : begin-expression-statement attribute-specifier-seq? expression-statement')
@glrp.rule('init-statement : begin-declaration simple-declaration')
@cxx98
def init_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? not allowed here
    pass


@glrp.rule('condition : begin-expression-statement attribute-specifier-seq? expression')
@glrp.rule(
    'condition : begin-declaration attribute-specifier-seq? [no-merge-warning] decl-specifier-seq begin-declarator-initializer declarator brace-or-equal-initializer'
)
@cxx98
def condition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.rule('condition? : begin-expression-statement attribute-specifier-seq? expression')
@glrp.rule(
    'condition? : begin-declaration  attribute-specifier-seq? [no-merge-warning] decl-specifier-seq begin-declarator-initializer declarator brace-or-equal-initializer'
)
@glrp.rule('condition? :')
@cxx98
def condition_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.rule('begin-expression-statement : [split:expression_statement]')
@cxx98
def begin_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-init-statement : [split:init_statement]')
@cxx98
def begin_init_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('condition')
@cxx98_merge
def ambiguous_condition(self, expression_statement, simple_declaration):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('condition')
@cxx98_merge
def ambiguous_condition_2(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('condition?')
@cxx98_merge
def ambiguous_condition_opt(self, expression_statement, simple_declaration):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('condition?')
@cxx98_merge
def ambiguous_condition_opt_2(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('init-statement')
@cxx98_merge
def ambiguous_init_statement(self, expression_statement, simple_declaration):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('statement')
@cxx98_merge
def ambiguous_statement(self, expression_statement, simple_declaration):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser