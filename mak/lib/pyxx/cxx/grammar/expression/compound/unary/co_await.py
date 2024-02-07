"""
await-expression:
    co_await cast-expression
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx20
from ......ast.expressions import AwaitExpression


@glrp.rule('constant-expression[prec:right,15] : [prec:right,15]"co_await" constant-expression')
@glrp.rule('constant-expression#[prec:right,15] : [prec:right,15]"co_await" constant-expression#')
@cxx20
def await_expression_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return AwaitExpression(p[1])
