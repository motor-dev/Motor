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
from .....ast.expressions import AmbiguousExpression, FoldExpressionLeft, FoldExpressionRight, FoldExpressionBoth
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
    return p[0].text()


@glrp.merge('fold-expression')
@cxx17_merge
def ambiguous_cast_expression_proxy(self, id_nontemplate, id_template):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    all_exprs = id_nontemplate + id_template
    if len(all_exprs) == 1:
        return all_exprs[0]
    else:
        return AmbiguousExpression(all_exprs)


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser
