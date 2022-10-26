"""
expression:
    assignment-expression
    expression , assignment-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from .....ast.expressions import BinaryExpression, AmbiguousExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('expression : expression-proxy')
@glrp.rule('expression? : expression')
@cxx98
def expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('expression-proxy : assignment-expression')
@cxx98
def expression_proxy_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('expression-proxy : expression-proxy "," assignment-expression')
@cxx98
def expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.rule('expression? : ')
@cxx98
def expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.merge('expression-proxy')
@cxx98_merge
def ambiguous_expression(self, ambiguous_expression, ambiguous_relational_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    all_exprs = ambiguous_expression + ambiguous_relational_expression
    return AmbiguousExpression(all_exprs)


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser