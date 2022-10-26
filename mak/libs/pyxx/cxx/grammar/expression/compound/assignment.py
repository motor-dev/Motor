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
from ....parser import cxx98, cxx20
from .....ast.expressions import BinaryExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('assignment-expression : conditional-expression')
@glrp.rule('assignment-expression : throw-expression')
@glrp.rule('assignment-expression? : conditional-expression')
@glrp.rule('assignment-expression? : throw-expression')
@cxx98
def assignment_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('assignment-expression : logical-or-expression assignment-operator initializer-clause')
@glrp.rule('assignment-expression? : logical-or-expression assignment-operator initializer-clause')
@cxx98
def assignment_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('assignment-expression : yield-expression')
@glrp.rule('assignment-expression? : yield-expression')
@cxx20
def assignment_expression_stop_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('assignment-expression? :')
@cxx20
def assignment_expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('assignment-operator : [prec:left,1]"="')
@glrp.rule('assignment-operator : "*="')
@glrp.rule('assignment-operator : "/="')
@glrp.rule('assignment-operator : "%="')
@glrp.rule('assignment-operator : "+="')
@glrp.rule('assignment-operator : "-="')
@glrp.rule('assignment-operator : ">>="')
@glrp.rule('assignment-operator : "<<="')
@glrp.rule('assignment-operator : "&="')
@glrp.rule('assignment-operator : "^="')
@glrp.rule('assignment-operator : "|="')
@cxx98
def assignment_operator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser