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
@glrp.rule('statement : begin-expression-statement attribute-specifier-seq? expression-statement')
@glrp.rule('statement : attribute-specifier-seq? compound-statement')
@glrp.rule('statement : attribute-specifier-seq? selection-statement')
@glrp.rule('statement : attribute-specifier-seq? iteration-statement')
@glrp.rule('statement : attribute-specifier-seq? jump-statement')
@glrp.rule('statement : declaration-statement')
@glrp.rule('statement : attribute-specifier-seq? try-block')
@cxx98
def statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('init-statement : begin-expression-statement attribute-specifier-seq? expression-statement')
@glrp.rule('init-statement : simple-declaration')
@cxx98
def init_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? not allowed here
    pass


@glrp.rule('condition : begin-expression-statement attribute-specifier-seq? expression')
@glrp.rule(
    'condition : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq begin-declarator-initializer declarator brace-or-equal-initializer'
)
@cxx98
def condition(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.rule('condition? : begin-expression-statement attribute-specifier-seq? expression')
@glrp.rule(
    'condition? : begin-simple-declaration attribute-specifier-seq? decl-specifier-seq begin-declarator-initializer declarator brace-or-equal-initializer'
)
@glrp.rule('condition? :')
@cxx98
def condition_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.rule('begin-expression-statement : [split:expression_statement]')
@cxx98
def begin_expression_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.merge('statement')
@cxx98_merge
def ambiguous_statement(self, expression_statement, ambiguous_block_declaration):
    # type: (CxxParser, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser