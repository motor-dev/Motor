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
@glrp.rule('statement : attribute-specifier-seq? expression-statement')
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


@glrp.rule('init-statement : attribute-specifier-seq? expression-statement')
@glrp.rule('init-statement : simple-declaration')
@cxx98
def init_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? not allowed here
    pass


@glrp.rule('condition : attribute-specifier-seq? expression')
@glrp.rule('condition : attribute-specifier-seq? decl-specifier-seq declarator brace-or-equal-initializer')
@cxx98
def condition(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.rule('condition? : attribute-specifier-seq? expression')
@glrp.rule('condition? : attribute-specifier-seq? decl-specifier-seq declarator brace-or-equal-initializer')
@glrp.rule('condition? :')
@cxx98
def condition_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    # TODO: attribute-specifier-seq? expression attribute-specifier-seq should be empty
    pass


@glrp.merge('condition')
@cxx98_merge
def ambiguous_condition(self, ambiguous_type_specifier, ambiguous_cast_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('condition?')
@cxx98_merge
def ambiguous_condition_opt(self, ambiguous_type_specifier, ambiguous_cast_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('init-statement')
@cxx98_merge
def ambiguous_init_statement(self, ambiguous_type_specifier, ambiguous_cast_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('statement')
@cxx98_merge
def ambiguous_statement(self, ambiguous_block_declaration, ambiguous_cast_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ...parser import CxxParser