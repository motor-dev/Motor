"""
assignment-expression:
    conditional-expression
    yield-expression
    throw-expression
    logical-or-expression assignment-operator initializer-clause

assignment-operator: one of
    =  *=  /=  %=   +=  -=  >>=  <<=  &=  ^=  |=
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx20
from .....ast.expressions import BinaryExpression


@glrp.rule('assignment-expression : constant-expression')
@glrp.rule('assignment-expression# : constant-expression#')
@glrp.rule('assignment-expression? : constant-expression')
@glrp.rule('assignment-expression#? : "constant-expression#"')
@cxx98
def assignment_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('assignment-expression : constant-expression assignment-operator initializer-clause')
@glrp.rule('assignment-expression# : constant-expression# assignment-operator "initializer-clause#"')
@glrp.rule('assignment-expression? : constant-expression assignment-operator initializer-clause')
@glrp.rule('assignment-expression#? : constant-expression# assignment-operator "initializer-clause#"')
@cxx98
def assignment_expression(self: CxxParser, p: glrp.Production) -> Any:
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('assignment-expression? :')
@glrp.rule('assignment-expression#? :')
@cxx98
def assignment_expression_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('assignment-operator : [prec:right,2]"="')
@glrp.rule('assignment-operator : [prec:right,2]"*="')
@glrp.rule('assignment-operator : [prec:right,2]"/="')
@glrp.rule('assignment-operator : [prec:right,2]"%="')
@glrp.rule('assignment-operator : [prec:right,2]"+="')
@glrp.rule('assignment-operator : [prec:right,2]"-="')
@glrp.rule('assignment-operator : [prec:right,2]">>="')
@glrp.rule('assignment-operator : [prec:right,2]"<<="')
@glrp.rule('assignment-operator : [prec:right,2]"&="')
@glrp.rule('assignment-operator : [prec:right,2]"^="')
@glrp.rule('assignment-operator : [prec:right,2]"|="')
@cxx98
def assignment_operator(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]
