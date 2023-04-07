"""
yield-expression:
    co_yield assignment-expression
    co_yield braced-init-list
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx20
from .....ast.expressions import YieldExpression


@glrp.rule('yield-expression : "co_yield" assignment-expression')
@glrp.rule('"yield-expression#" : "co_yield" "assignment-expression#"')
@cxx20
def yield_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return YieldExpression(p[1])


@glrp.rule('yield-expression : "co_yield" braced-init-list')
@glrp.rule('"yield-expression#" : "co_yield" braced-init-list')
@cxx20
def yield_expression_braced_init_list_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return YieldExpression(p[1])
