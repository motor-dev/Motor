"""
noexcept-expression:
    noexcept ( expression )
"""

import glrp
from .....parse import cxx11
from ......ast.expressions import NoexceptExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('noexcept-expression : "noexcept" "(" expression ")"')
@cxx11
def noexcept_expression_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NoexceptExpression(p[2])


if TYPE_CHECKING:
    from typing import Any
    from .....parse import CxxParser