"""
compare-expression:
    shift-expression
    compare-expression <=> shift-expression
"""

import glrp
from ....parser import cxx98, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('compare-expression : shift-expression')
@cxx98
def compare_expression(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('compare-expression : compare-expression "<=>" shift-expression')
@cxx20
def compare_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ....parser import CxxParser