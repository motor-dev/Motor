"""
selection-statement:
    if constexpr? ( init-statement? condition ) statement
    if constexpr? ( init-statement? condition ) statement else statement
    if !? consteval compound-statement
    if !? consteval compound-statement else statement
    switch ( init-statement? condition ) statement
"""

import glrp
from ...parser import cxx98, deprecated_cxx17, cxx17, cxx23, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('selection-statement : "switch" "(" condition ")" statement')
@glrp.rule('selection-statement : "switch" "(" init-statement condition ")" statement')
@cxx98
def selection_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('selection-statement : "if" "(" condition ")" statement')
@glrp.rule('selection-statement : "if" "(" condition ")" statement [prec:left,1]"else" statement')
@cxx98
@deprecated_cxx17
def selection_statement_if(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('selection-statement : "if" "constexpr"? "(" condition ")" statement')
@glrp.rule('selection-statement : "if" "constexpr"? "(" condition ")" statement [prec:left,1]"else" statement')
@glrp.rule('selection-statement : "if" "constexpr"? "(" init-statement condition ")" statement')
@glrp.rule(
    'selection-statement : "if" "constexpr"? "(" init-statement condition ")" statement [prec:left,1]"else" statement'
)
@cxx17
def selection_statement_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('constexpr? : "constexpr"')
@glrp.rule('constexpr? : ')
@cxx17
def constexpr_opt_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('selection-statement : "if" "!"? "consteval" compound-statement')
@glrp.rule('selection-statement : "if" "!"? "consteval" compound-statement [prec:left,1]"else" statement')
@cxx23
def selection_statement_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('"!"? : "!"')
@glrp.rule('"!"? :')
@cxx23
def not_opt_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('selection-statement')
@cxx98_merge
def ambiguous_selection_statement(self, ambiguous_condition, ambiguous_init_statement):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    # switch(init-statement condition) vs switch(condition)
    # if(init-statement condition) vs switch(condition)
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ...parser import CxxParser