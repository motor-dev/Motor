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
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('cast-expression')
@cxx98_merge
def ambiguous_cast_expression(self, type_id, ambiguous_primary_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser