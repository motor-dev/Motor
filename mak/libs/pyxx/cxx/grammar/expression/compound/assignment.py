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
from motor_typing import TYPE_CHECKING


@glrp.rule('assignment-expression : conditional-expression')
@glrp.rule('assignment-expression : throw-expression')
@glrp.rule('assignment-expression : logical-or-expression assignment-operator initializer-clause')
@cxx98
def assignment_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('assignment-expression : yield-expression')
@cxx20
def assignment_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('assignment-expression? :')
@glrp.rule('assignment-expression? : conditional-expression')
@glrp.rule('assignment-expression? : throw-expression')
@glrp.rule('assignment-expression? : logical-or-expression assignment-operator initializer-clause')
@cxx98
def assignment_expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('assignment-expression? : yield-expression')
@cxx20
def assignment_expression_opt_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('assignment-operator : [prec:left,0]"="')
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
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser