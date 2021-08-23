"""
selection-statement:
    if constexpr? ( init-statement? condition ) statement
    if constexpr? ( init-statement? condition ) statement else statement
    if !? consteval compound-statement
    if !? consteval compound-statement else statement
    switch ( init-statement? condition ) statement
"""

import glrp
from ...parser import cxx98, cxx17, cxx23
from motor_typing import TYPE_CHECKING


@glrp.rule('selection-statement[prec:left,0] : "if" "(" condition ")" statement')
@glrp.rule('selection-statement : "if" "(" condition ")" statement [prec:left,0]"else" statement')
@glrp.rule('selection-statement : "switch" "(" init-statement? condition ")" statement')
@cxx98
def selection_statement(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('selection-statement[prec:left,0] : "if" "constexpr" "(" init-statement? condition ")" statement')
@glrp.rule('selection-statement[prec:left,0] : "if" "(" init-statement condition ")" statement')
@glrp.rule(
    'selection-statement : "if" "constexpr" "(" init-statement? condition ")" statement [prec:left,0]"else" statement'
)
@glrp.rule('selection-statement : "if" "(" init-statement condition ")" statement [prec:left,0]"else" statement')
@cxx17
def selection_statement_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('selection-statement[prec:left,0] : "if" "!"? "consteval" compound-statement')
@glrp.rule('selection-statement : "if" "!"? "consteval" compound-statement [prec:left,0]"else" statement')
@cxx23
def selection_statement_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser