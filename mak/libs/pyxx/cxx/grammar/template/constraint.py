"""
constraint-expression:
    logical-or-expression
"""

import glrp
from ...parser import cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('constraint-expression : logical-or-expression')
@cxx20
def constraint_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


if TYPE_CHECKING:
    from ...parser import CxxParser