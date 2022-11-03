"""
shift-expression:
    additive-expression
    shift-expression << additive-expression
    shift-expression >> additive-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from .....ast.expressions import BinaryExpression, AmbiguousExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('shift-expression : additive-expression')
@cxx98
def shift_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('shift-expression : shift-expression "<<" additive-expression')
@glrp.rule('shift-expression : shift-expression ">>" additive-expression')
@cxx98
def shift_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BinaryExpression(p[0], p[2], p[1].text())


@glrp.merge('shift-expression')
@cxx98_merge
def ambiguous_shift_expression(self, ambiguous_type_id, ambiguous_shift_expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    expressions = ambiguous_type_id + ambiguous_shift_expression
    return AmbiguousExpression(expressions)


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser