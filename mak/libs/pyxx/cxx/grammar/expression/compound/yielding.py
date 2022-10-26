"""
yield-expression:
    co_yield assignment-expression
    co_yield braced-init-list
"""

import glrp
from ....parser import cxx20
from .....ast.expressions import YieldExpression, LiteralExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('yield-expression : "co_yield" assignment-expression')
@cxx20
def yield_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return YieldExpression(p[1])


@glrp.rule('yield-expression : "co_yield" braced-init-list')
@cxx20
def yield_expression_braced_init_list_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return YieldExpression(LiteralExpression(p[1]))


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser