"""
await-expression:
    co_await cast-expression
"""

import glrp
from .....parser import cxx20
from ......ast.expressions import AwaitExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('await-expression : "co_await" cast-expression')
@cxx20
def await_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return AwaitExpression(p[1])


if TYPE_CHECKING:
    from typing import Any
    from .....parser import CxxParser