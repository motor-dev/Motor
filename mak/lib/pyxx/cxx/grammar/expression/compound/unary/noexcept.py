"""
noexcept-expression:
    noexcept ( expression )
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx11
from ......ast.expressions import NoexceptExpression, ErrorExpression


@glrp.rule('constant-expression : "noexcept" "(" expression ")"')
@glrp.rule('constant-expression# : "noexcept" "(" expression ")"')
@cxx11
def noexcept_expression_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return NoexceptExpression(p[2])


@glrp.rule('constant-expression : "noexcept" "(" "#error" ")"')
@glrp.rule('constant-expression# : "noexcept" "(" "#error" ")"')
@cxx11
def noexcept_expression_error_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()
