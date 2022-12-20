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
from ....parse import cxx17
from .....ast.expressions import FoldExpressionLeft, FoldExpressionRight, FoldExpressionBoth
from motor_typing import TYPE_CHECKING


@glrp.rule('fold-expression : "(" begin-fold-expression [no-merge-warning] cast-expression fold-operator "..." ")"')
@cxx17
def fold_expression_left_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return FoldExpressionLeft(p[2], p[3])


@glrp.rule('fold-expression : "(" begin-fold-expression "..." fold-operator cast-expression ")"')
@cxx17
def fold_expression_right_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return FoldExpressionRight(p[4], p[3])


@glrp.rule(
    'fold-expression : "(" begin-fold-expression [no-merge-warning] cast-expression fold-operator "..." fold-operator cast-expression ")"'
)
@cxx17
def fold_expression_both_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return FoldExpressionBoth(p[2], p[3], p[6], p[5])


@glrp.rule('begin-fold-expression: [split:fold_expression]')
@cxx17
def begin_fold_expression_cxx17(self, p):
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
    return p[0].text()


@glrp.rule('fold-operator : ">>"')
@cxx17
def fold_operator_rshift_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser
