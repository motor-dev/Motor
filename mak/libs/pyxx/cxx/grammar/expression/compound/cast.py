"""
cast-expression:
    unary-expression
    ( type-id ) cast-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('cast-expression : unary-expression')
@glrp.rule('cast-expression : "(" begin-type-id type-id ")" cast-expression')
@cxx98
def cast_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser