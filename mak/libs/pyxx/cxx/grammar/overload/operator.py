"""
operator-function-id:
    operator operator

operator: one of
    new      delete   new[]    delete[] co_await ()       []       ->       ->*
    ~        !        +        -        *        /        %        ^        &
    |        =        +=       -=       *=       /=       %=       ^=       &=
    |=       ==       !=       <        >        <=       >=       <=>      &&
    ||       <<       >>       <<=      >>=      ++       --       ,
"""

import glrp
from ...parser import cxx98, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('operator-function-id : "operator" overloadable-operator')
@cxx98
def operator_function_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('overloadable-operator : "new"    ')
@glrp.rule('overloadable-operator : "delete" ')
@glrp.rule('overloadable-operator : "new"    [prec:left,1]"[" "]"')
@glrp.rule('overloadable-operator : "delete" [prec:left,1]"[" "]"')
@glrp.rule('overloadable-operator : "(" ")"')
@glrp.rule('overloadable-operator : "[" "]"')
@glrp.rule('overloadable-operator : "->"')
@glrp.rule('overloadable-operator : "->*"')
@glrp.rule('overloadable-operator : "~"')
@glrp.rule('overloadable-operator : "!"')
@glrp.rule('overloadable-operator : "+"')
@glrp.rule('overloadable-operator : "-"')
@glrp.rule('overloadable-operator : "*"')
@glrp.rule('overloadable-operator : "/"')
@glrp.rule('overloadable-operator : "%"')
@glrp.rule('overloadable-operator : "^"')
@glrp.rule('overloadable-operator : "&"')
@glrp.rule('overloadable-operator : "|"')
@glrp.rule('overloadable-operator : "="')
@glrp.rule('overloadable-operator : "+="')
@glrp.rule('overloadable-operator : "-="')
@glrp.rule('overloadable-operator : "*="')
@glrp.rule('overloadable-operator : "/="')
@glrp.rule('overloadable-operator : "%="')
@glrp.rule('overloadable-operator : "^="')
@glrp.rule('overloadable-operator : "&="')
@glrp.rule('overloadable-operator : "|="')
@glrp.rule('overloadable-operator : "=="')
@glrp.rule('overloadable-operator : "!="')
@glrp.rule('overloadable-operator : "<"')
@glrp.rule('overloadable-operator : ">"')
@glrp.rule('overloadable-operator : "<="')
@glrp.rule('overloadable-operator : ">="')
@glrp.rule('overloadable-operator : "&&"')
@glrp.rule('overloadable-operator : "||"')
@glrp.rule('overloadable-operator : "<<"')
@glrp.rule('overloadable-operator : ">>"')
@glrp.rule('overloadable-operator : "<<="')
@glrp.rule('overloadable-operator : ">>="')
@glrp.rule('overloadable-operator : "++"')
@glrp.rule('overloadable-operator : "--"')
@glrp.rule('overloadable-operator : ","')
@cxx98
def overloadable_operator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('overloadable-operator : "co_await"')
@glrp.rule('overloadable-operator : "<=>"')
@cxx20
def overloadable_operator_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser