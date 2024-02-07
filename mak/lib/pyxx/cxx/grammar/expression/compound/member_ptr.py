"""
pm-expression:
    cast-expression
    pm-expression .* cast-expression
    pm-expression ->* cast-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98
from .....ast.expressions import MemberPtrExpression


@glrp.rule('constant-expression[prec:left,14] : constant-expression [prec:left,14]".*" constant-expression')
@glrp.rule('constant-expression[prec:left,14] : constant-expression [prec:left,14]"->*" constant-expression')
@glrp.rule('constant-expression#[prec:left,14] : constant-expression# [prec:left,14]".*" constant-expression#')
@glrp.rule('constant-expression#[prec:left,14] : constant-expression# [prec:left,14]"->*" constant-expression#')
@cxx98
def pm_expression(self: CxxParser, p: glrp.Production) -> Any:
    return MemberPtrExpression(p[0], p[2], p[1].text())
