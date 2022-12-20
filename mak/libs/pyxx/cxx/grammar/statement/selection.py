"""
selection-statement:
    if constexpr? ( init-statement? condition ) statement
    if constexpr? ( init-statement? condition ) statement else statement
    if !? consteval compound-statement
    if !? consteval compound-statement else statement
    switch ( init-statement? condition ) statement
"""

import glrp
from ...parse import cxx98, cxx17, cxx23, cxx98_merge
from ....ast.statements import SwitchStatement, IfStatement, IfConstevalStatement, SelectionCondition, AmbiguousSelectionCondition
from motor_typing import TYPE_CHECKING


@glrp.rule('selection-statement : "switch" "(" selection-condition ")" statement')
@cxx98
def selection_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SwitchStatement(p[2], p[4])


@glrp.rule('selection-statement : "if" "(" selection-condition ")" statement')
@cxx98
def selection_statement_if(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IfStatement(p[2], p[4], None, False)


@glrp.rule('selection-statement : "if" "(" selection-condition ")" statement [prec:left,1]"else" statement')
@cxx98
def selection_statement_ifelse(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IfStatement(p[2], p[4], p[6], False)


@glrp.rule('selection-statement : "if" "constexpr" "(" selection-condition ")" statement')
@cxx17
def selection_statement_if_constexpr_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IfStatement(p[2], p[4], None, True)


@glrp.rule('selection-statement : "if" "constexpr" "(" selection-condition ")" statement [prec:left,1]"else" statement')
@cxx17
def selection_statement_if_constexpr_else_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IfStatement(p[2], p[4], p[6], True)


@glrp.rule('selection-statement : "if" "!"? "consteval" compound-statement')
@cxx23
def selection_statement_if_consteval_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IfConstevalStatement(p[1], p[3], None)


@glrp.rule('selection-statement : "if" "!"? "consteval" compound-statement [prec:left,1]"else" statement')
@cxx23
def selection_statement_consteval_else_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IfConstevalStatement(p[1], p[3], p[5])


@glrp.rule('selection-condition : condition')
@cxx98
def selection_condition(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SelectionCondition(None, p[0])


@glrp.rule('selection-condition : init-statement condition')
@cxx17
def selection_condition_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SelectionCondition(p[0], p[1])


@glrp.rule('"!"? : "!"')
@cxx23
def not_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return True


@glrp.rule('"!"? :')
@cxx23
def not_opt_cxx23(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return False


@glrp.merge('selection-condition')
@cxx98_merge
def ambiguous_selection_condition(self, ambiguous_init_statement, ambiguous_condition):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousSelectionCondition(ambiguous_init_statement + ambiguous_condition)


@glrp.merge('selection-condition')
@cxx98_merge
def ambiguous_selection_condition_2(self, ambiguous_simple_declaration, ambiguous_condition_2):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousSelectionCondition(ambiguous_simple_declaration + ambiguous_condition_2)


@glrp.merge('selection-condition')
@cxx98_merge
def ambiguous_selection_condition_3(self, continue_declarator_list, ambiguous_init_declarator_initializer):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousSelectionCondition(continue_declarator_list + ambiguous_init_declarator_initializer)


if TYPE_CHECKING:
    from typing import Any, List
    from ...parse import CxxParser