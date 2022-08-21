"""
cast-expression:
    unary-expression
    ( type-id ) cast-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('cast-expression : unary-expression')
@glrp.rule('cast-expression : "(" type-id ")" cast-expression')
@cxx98
def cast_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('cast-expression')
@cxx98_merge
def ambiguous_cast_expression(self, ambiguous_type_id, generic_postfix_expression, ambiguous_cast_expression):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser