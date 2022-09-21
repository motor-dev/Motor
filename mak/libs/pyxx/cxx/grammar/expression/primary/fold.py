"""
fold-expression:
    ( cast-expression fold-operator ... )
    ( ... fold-operator cast-expression )
    ( cast-expression fold-operator ... fold-operator cast-expression )

fold-operator: one of
+   -   *   /   %   ^   &   |   <<  >>
+=  -=  *=  /=  %=  ^=  &=  |=  <<= >>= =
==  !=  <   >   <=  >=  &&  ||  ,   .*  ->*
"""

import glrp
from ....parser import cxx17, cxx17_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('fold-expression : "(" begin-fold-expression cast-expression-proxy fold-operator "..." ")"')
@glrp.rule('fold-expression : "(" begin-fold-expression "..." fold-operator cast-expression-proxy ")"')
@glrp.rule(
    'fold-expression : "(" begin-fold-expression cast-expression-proxy fold-operator "..." fold-operator cast-expression-proxy ")"'
)
@cxx17
def fold_expression_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-fold-expression: [split:fold_expression]')
@cxx17
def begin_fold_expression_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('cast-expression-proxy : cast-expression')
@cxx17
def cast_expression_expression_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('fold-operator : "+"')
@glrp.rule('fold-operator : "-"')
@glrp.rule('fold-operator : "*"')
@glrp.rule('fold-operator : "/"')
@glrp.rule('fold-operator : "%"')
@glrp.rule('fold-operator : "^"')
@glrp.rule('fold-operator : "&"')
@glrp.rule('fold-operator : "|"')
@glrp.rule('fold-operator : "<<"')
@glrp.rule('fold-operator : ">>"')
@glrp.rule('fold-operator : "+="')
@glrp.rule('fold-operator : "-="')
@glrp.rule('fold-operator : "*="')
@glrp.rule('fold-operator : "/="')
@glrp.rule('fold-operator : "%="')
@glrp.rule('fold-operator : "^="')
@glrp.rule('fold-operator : "&="')
@glrp.rule('fold-operator : "|="')
@glrp.rule('fold-operator : "<<="')
@glrp.rule('fold-operator : ">>="')
@glrp.rule('fold-operator : "="')
@glrp.rule('fold-operator : "=="')
@glrp.rule('fold-operator : "!="')
@glrp.rule('fold-operator : "<"')
@glrp.rule('fold-operator : ">"')
@glrp.rule('fold-operator : "<="')
@glrp.rule('fold-operator : ">="')
@glrp.rule('fold-operator : "&&"')
@glrp.rule('fold-operator : "||"')
@glrp.rule('fold-operator : ","')
@glrp.rule('fold-operator : ".*"')
@glrp.rule('fold-operator : "->*"')
@cxx17
def fold_operator_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('cast-expression-proxy')
@cxx17_merge
def ambiguous_cast_expression_proxy(self, ambiguous_postfix_expression, id_template):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser
