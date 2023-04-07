"""
noexcept-expression:
    noexcept ( expression )
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx11
from ......ast.expressions import NoexceptExpression, ErrorExpression


@glrp.rule('noexcept-expression : "noexcept" "(" expression ")"')
@cxx11
def noexcept_expression_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return NoexceptExpression(p[2])


@glrp.rule('noexcept-expression : "noexcept" "(" "#error" ")"')
@cxx11
def noexcept_expression_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
