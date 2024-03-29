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
from typing import Any
from ....parse import CxxParser, cxx17, cxx20
from .....ast.expressions import FoldExpressionLeft, FoldExpressionRight, FoldExpressionBoth, ErrorExpression


@glrp.rule(
    'constant-expression : [prec:right,15]"(" begin-fold-expression constant-expression fold-operator "..." ")"')
@glrp.rule(
    '"constant-expression#" : [prec:right,15]"(" begin-fold-expression constant-expression fold-operator "..." ")"')
@cxx17
def fold_expression_left_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return FoldExpressionLeft(p[2], p[3])


@glrp.rule('constant-expression : [prec:right,15]"(" begin-fold-expression "..." fold-operator constant-expression ")"')
@glrp.rule(
    '"constant-expression#" : [prec:right,15]"(" begin-fold-expression "..." fold-operator constant-expression ")"')
@cxx17
def fold_expression_right_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return FoldExpressionRight(p[4], p[3])


@glrp.rule(
    'constant-expression : [prec:right,15]"(" begin-fold-expression constant-expression fold-operator "..." fold-operator constant-expression ")"'
)
@glrp.rule(
    '"constant-expression#" : [prec:right,15]"(" begin-fold-expression constant-expression fold-operator "..." fold-operator constant-expression ")"'
)
@cxx17
def fold_expression_both_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return FoldExpressionBoth(p[2], p[3], p[6], p[5])


@glrp.rule('begin-fold-expression: [split:fold_expression]')
@cxx17
def begin_fold_expression_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    pass


@glrp.rule('constant-expression : [prec:right,15]"(" begin-fold-expression "#error" ")"')
@glrp.rule('constant-expression# : [prec:right,15]"(" begin-fold-expression "#error" ")"')
@cxx17
def fold_expression_error_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


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
def fold_operator_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()


@glrp.rule('fold-operator : ">>"')
@cxx17
def fold_operator_rshift_cxx17(self: CxxParser, p: glrp.Production) -> Any:
    return '>>'


@glrp.rule('fold-operator : "<=>"')
@cxx20
def fold_operator_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0].text()
