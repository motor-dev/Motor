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
from typing import Any
from ...parse import CxxParser, cxx98, cxx20
from ....ast.reference import OperatorId


@glrp.rule('operator-function-id : "operator" overloadable-operator')
@cxx98
def operator_function_id(self: CxxParser, p: glrp.Production) -> Any:
    return OperatorId(p[1])


@glrp.rule('overloadable-operator : "new"    ')
@glrp.rule('overloadable-operator : "delete" ')
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
@glrp.rule('overloadable-operator : "<<="')
@glrp.rule('overloadable-operator : ">>="')
@glrp.rule('overloadable-operator : "++"')
@glrp.rule('overloadable-operator : "--"')
@glrp.rule('overloadable-operator : ","')
@cxx98
def overloadable_operator(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()


@glrp.rule('overloadable-operator : ">>"')
@cxx98
def overloadable_operator_rshift(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('overloadable-operator : "new"    [prec:left,1]"[" "]"')
@glrp.rule('overloadable-operator : "delete" [prec:left,1]"[" "]"')
@cxx98
def overloadable_operator_array(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text() + '[]'


@glrp.rule('overloadable-operator : "(" ")"')
@glrp.rule('overloadable-operator : "[" "]"')
@cxx98
def overloadable_operator_bracket(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text() + p[1].text()


@glrp.rule('overloadable-operator : "co_await"')
@glrp.rule('overloadable-operator : "<=>"')
@cxx20
def overloadable_operator_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()
